import requests
import json
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.constants import SAMPLE_CORE_URL, \
    ALLOWED_RECORD_TYPES
from .helpers import validate, do_additional_checks, \
    get_validation_results_structure, get_record_name, join_issues


@app.task
def validate_against_schema(json_to_test):
    """
    Task to send json data to elixir-validator
    :param json_to_test: json to test against schema
    :return: all issues in dict
    """
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
    return validation_results


@app.task
def collect_warnings_and_additional_checks(json_to_test):
    """
    Task to do additional checks inside python app
    :param json_to_test: json to test against additional checks
    :return: all issues in dict
    """
    warnings_and_additional_checks_results = dict()
    for name, url in ALLOWED_RECORD_TYPES.items():
        warnings_and_additional_checks_results.setdefault(name, list())
        warnings_and_additional_checks_results[name] = \
            do_additional_checks(json_to_test[name], url, name)
    return warnings_and_additional_checks_results


@app.task
def join_validation_results(results):
    """
    This task will join results from previous two tasks
    :param results: list with results of previous two tasks
    :return: joined issues in dict
    """
    joined_results = dict()
    for record_type in results[0]:
        joined_results.setdefault(record_type, list())
        for index, first_record in enumerate(results[0][record_type]):
            second_record = results[1][record_type][index]
            tmp = get_validation_results_structure(first_record['name'])
            tmp = join_issues(tmp, first_record, second_record)
            joined_results[record_type].append(tmp)
    return joined_results
