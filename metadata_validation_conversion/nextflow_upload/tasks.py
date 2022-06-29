from abc import ABC

from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
import requests
import os
from celery import Task


class LogErrorsTask(Task, ABC):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        send_message(room_id=args[0], submission_message='Error with file upload',
                     errors=f'Error: {exc}')


@app.task(base=LogErrorsTask)
def upload_to_nginx(fileid, dir_name, filename):
    send_message(submission_message="Uploading file", room_id=fileid)
    filepath = f'/data/{fileid}'
    url = 'http://nginx-svc:80/files_upload'
    download_url = f'https://api.faang.org/files/nextflow_files/{dir_name}/{filename}'
    data = {
        'path': f'nextflow_files/{dir_name}',
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
        # backup to s3
        cmd = f"aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 cp " \
            f"{filepath} s3://nextflow_files/{dir_name}/{filename}"
        os.system(cmd)
        return 'Success'
