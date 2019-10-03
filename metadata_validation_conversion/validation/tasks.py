import requests
import json
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.constants import SAMPLE_CORE_URL, \
    ALLOWED_RECORD_TYPES
from .helpers import validate, check_recommended_fields_are_present


@app.task
def validate_against_schema(json_to_test):
    core_schema = requests.get(SAMPLE_CORE_URL).json()
    validation_results = dict()
    for name, url in ALLOWED_RECORD_TYPES.items():
        type_schema = requests.get(url).json()
        del type_schema['properties']['samples_core']
        validation_results.setdefault(name, dict())
        validation_results[name].setdefault('core', list())
        validation_results[name].setdefault('type', list())
        for record in json_to_test[name]:
            validation_results[name]['core'].append(
                validate(record['samples_core'], core_schema))
            validation_results[name]['type'].append(
                validate(record, type_schema))
    return validation_results


@app.task
def collect_warnings_and_additional_checks(json_to_test):
    warnings_and_additional_checks_results = dict()

    for name, url in ALLOWED_RECORD_TYPES.items():
        warnings = check_recommended_fields_are_present(
            json_to_test[name], url, name)
        if len(warnings) > 0:
            print(warnings)
            print(len(warnings))
    return warnings_and_additional_checks_results
