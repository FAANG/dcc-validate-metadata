import datetime
from abc import ABC
from django.conf import settings
from elasticsearch import Elasticsearch, RequestsHttpConnection
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from metadata_validation_conversion.constants import ORGANIZATIONS, PROTOCOL_INDICES
import requests
import os
from celery import Task
    
es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection, \
                    http_auth=(settings.ES_USER, settings.ES_PASSWORD), \
                    use_ssl=True, verify_certs=True)

class LogErrorsTask(Task, ABC):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        send_message(room_id=kwargs['fileid'], submission_message='Error with protocol upload',
                     errors=f'Error: {exc}')


@app.task(base=LogErrorsTask)
def validate(filename, fileid, protocol_type):
    send_message(submission_message="Starting to validate file",
                 room_id=fileid)
    errors = list()
    if protocol_type in ['protocol_samples', 'protocol_analysis', 'protocol_files']:
        if es.exists(protocol_type, id=fileid):
            errors.append(f"File {filename[0]} already is in ES")
    else:
        errors.append(f"Protocol type for {filename[0]} is not protocol_samples/protocol_analysis/protocol_files")
    if filename[0] not in ORGANIZATIONS:
        errors.append(f"Your organization {filename[0]} was not found")
    if len(filename) < 2 or filename[1] != 'SOP':
        errors.append("Please add SOP tag in your protocol name")
    if '.pdf' not in filename[-1]:
        errors.append("Please use PDF format only")
    else:
        protocol_date = filename[-1].split('.pdf')[0]
        try:
            datetime.datetime.strptime(protocol_date, '%Y%m%d')
        except ValueError:
            errors.append("Incorrect date format, should be YYYYMMDD")
    if len(errors) != 0:
        send_message(submission_message="Upload failed, "
                                        "please contact "
                                        "faang-dcc@ebi.ac.uk",
                     errors=errors, room_id=fileid)
        return 'Error'
    else:
        return 'Success'


@app.task(base=LogErrorsTask)
def upload(validation_results, fileserver_path, filename, fileid):
    if validation_results == 'Success':
        send_message(submission_message="Uploading file", room_id=fileid)
        filepath = f"/data/{fileid}.pdf"
        url = 'http://nginx-svc:80/files_upload'
        download_url = f'https://api.faang.org/files/{fileserver_path}/{filename}'
        data = {
            'path': fileserver_path,
            'name': filename
        }
        res = requests.post(url, files={'file': open(filepath, 'rb')}, data=data)
        if res.status_code != 200:
            send_message(submission_message="Upload failed, "
                                            "please contact "
                                            "faang-dcc@ebi.ac.uk",
                         room_id=fileid)
            return 'Error'
        else:
            send_message(submission_message=f'Success! ' \
                 f'Please download your file at \n {download_url}', room_id=fileid)
            # backup to s3
            cmd = f"aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 cp " \
                  f"{filepath} s3://{fileserver_path}/{filename}"
            os.system(cmd)
            return 'Success'
    return 'Error'

@app.task(base=LogErrorsTask)
def add_to_es(upload_results, protocol_type, protocol_file, fileid):
    try:
        if upload_results == 'Success':
            index = PROTOCOL_INDICES[protocol_type]
            key = requests.utils.unquote(protocol_file)
            url = f"https://api.faang.org/files/protocols/{protocol_type}/{protocol_file}"
            parsed = protocol_file.strip().split("_")
            # Parsing protocol name
            if 'SOP' in parsed:
                protocol_name = requests.utils.unquote(" ".join(parsed[2:-1]))
            else:
                protocol_name = requests.utils.unquote(" ".join(parsed[1:-1]))
            if index == 'protocol_samples' or index == 'protocol_analysis':
                if not es.exists(index, id=key):
                    # Parsing university name
                    if parsed[0] == 'WUR':
                        university_name = 'WUR'
                    elif parsed[0] not in ORGANIZATIONS:
                        university_name = None
                    else:
                        university_name = ORGANIZATIONS[parsed[0]]
                    # Parsing date
                    date = parsed[-1].split(".pdf")[0][:4]
                    protocol_data = {
                        "universityName": university_name,
                        "protocolDate": date,
                        "protocolName": protocol_name, 
                        "key": key,
                        "url": url
                    }
                    if index == 'protocol_samples':
                        protocol_data["specimens"] = []
                    elif index == 'protocol_analysis':
                        protocol_data["analyses"] = []
                    es.index(index, id=key, body=protocol_data)
                    send_message(submission_message=f"Please download your file at \n {url}.\n" \
                                 f"Protocol added to data portal!", room_id=fileid)
            else:
                r = requests.get(f"http://backend-svc:8000/data/protocol_files/_search/?search={protocol_file}").json()
                if (r['hits']['total']['value'] == 0):
                    protocol_data = {
                        "experiments": [],
                        "experimentTarget": "",
                        "assayType": "",
                        "name": protocol_name,
                        "filename": key,
                        "key": key,
                        "url": url
                    }
                    es.index(index, id=key, body=protocol_data)
                    send_message(submission_message=f"Please download your file at \n {url}.\n" \
                                 f"Protocol added to data portal!", room_id=fileid)
            status = 'Success'
        else:
            status = 'Error'
    except Exception as e:
        send_message(submission_message=f"Error adding new protocol, "
                     f"please contact faang-dcc@ebi.ac.uk", room_id=fileid)
        status = 'Error'
    finally:
        return status