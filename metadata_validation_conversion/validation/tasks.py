from metadata_validation_conversion.celery import app
from .helpers import validate


@app.task
def validate_against_schema(json_to_test):
    for organism in json_to_test['organism']:
        validate(organism['samples_core'])
    return "Success!!!"
