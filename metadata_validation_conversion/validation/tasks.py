import requests
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.constants import SAMPLE_CORE_URL, \
    ALLOWED_RECORD_TYPES
from .helpers import validate


@app.task
def validate_against_schema(json_to_test):
    schema = requests.get(SAMPLE_CORE_URL).json()
    for name in ALLOWED_RECORD_TYPES:
        for record in json_to_test[name]:
            validate(record['samples_core'], schema)
    return "Success!!!"
