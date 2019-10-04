import requests
import json
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.constants import SAMPLE_CORE_URL, \
    ALLOWED_RECORD_TYPES
from .helpers import validate, check_recommended_fields_are_present, \
    get_validation_results_structure, get_record_name

@app.task
def validate_against_schema(json_to_test):
    core_schema = requests.get(SAMPLE_CORE_URL).json()
    validation_results = dict()
    for name, url in ALLOWED_RECORD_TYPES.items():
        validation_results.setdefault(name, list())
        type_schema = requests.get(url).json()
        del type_schema['properties']['samples_core']
        for index, record in enumerate(json_to_test[name]):
            record_name = get_record_name(record['custom'], index)
            tmp = get_validation_results_structure(record_name)
            tmp['core']['errors'] = validate(record['samples_core'],
                                             core_schema)
            tmp['type']['errors'] = validate(record, type_schema)
            validation_results[name].append(tmp)
    print(json.dumps(validation_results))
    return validation_results


@app.task
def collect_warnings_and_additional_checks(json_to_test):
    warnings_and_additional_checks_results = dict()
    for name, url in ALLOWED_RECORD_TYPES.items():
        warnings_and_additional_checks_results.setdefault(name, list())
        warnings = check_recommended_fields_are_present(
            json_to_test[name], url, name)
        if len(warnings) > 0:
            print(warnings)
            print(len(warnings))
    return warnings_and_additional_checks_results
