from decouple import config
from metadata_validation_conversion.celery import app
from .FireAPI import FireAPI


@app.task
def upload():
    username = config('USERNAME')
    password = config('PASSWORD')
    archive_name = config('ARCHIVE_NAME')
    api_endpoint = config('API_ENDPOINT')
    fire_api_object = FireAPI(username, password, archive_name, api_endpoint)
    fire_api_object.upload_object()
    return 'Success'
