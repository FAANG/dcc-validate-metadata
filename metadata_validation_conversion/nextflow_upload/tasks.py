from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
import requests
import os


@app.task
def upload_to_nginx(fileid, dir_name, filename):
    send_message(submission_message="Uploading file", room_id=fileid)
    filepath = f'/data/{fileid}'
    url = 'http://nginx-svc:80/nextflow_upload'
    download_url = f'https://api.faang.org/nextflow_files_upload/{dir_name}/{filename}'
    data = {
        'path': dir_name,
        'name': filename
    }
    res = requests.post(url, files={'file': open(filepath,'rb')}, data=data)
    if res.status_code != 200:
        send_message(submission_message="Upload failed, "
                                        "please contact "
                                        "faang-dcc@ebi.ac.uk",
                        room_id=fileid)
        return 'Error'
    else:
        send_message(submission_message=f'Success! Please download your file at \n {download_url}', room_id=fileid)
        return 'Success'
