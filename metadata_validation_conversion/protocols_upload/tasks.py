import datetime
from abc import ABC

from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from metadata_validation_conversion.constants import ORGANIZATIONS
import requests
import os
from celery import Task


class LogErrorsTask(Task, ABC):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        send_message(room_id=kwargs['fileid'], submission_message='Error with protocol upload',
                     errors=f'Error: {exc}')


@app.task(base=LogErrorsTask)
def validate(filename, fileid):
    send_message(submission_message="Starting to validate file",
                 room_id=fileid)
    errors = list()
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
            send_message(submission_message='Success', room_id=fileid)
            # backup to s3
            cmd = f"aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 cp " \
                  f"{filepath} s3://{fileserver_path}/{filename}"
            os.system(cmd)
            return 'Success'
    return 'Error'
