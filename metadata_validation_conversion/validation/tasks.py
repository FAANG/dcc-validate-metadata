import json
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.constants import ALLOWED_RECORD_TYPES
from .helpers import do_additional_checks, collect_relationships, \
    check_relationships
from .get_biosample_data_async import fetch_biosample_data_for_ids
from .ElixirValidatorResults import ElixirValidatorResults
from .JoinedResults import JoinedResults


@app.task
def validate_against_schema(json_to_test):
    """
    Task to send json data to elixir-validator
    :param json_to_test: json to test against schema
    :return: all issues in dict
    """
    elixir_validation_results = ElixirValidatorResults(json_to_test)
    return elixir_validation_results.run_validation()


@app.task
def collect_warnings_and_additional_checks(json_to_test):
    """
    Task to do additional checks inside python app
    :param json_to_test: json to test against additional checks
    :return: all issues in dict
    """
    warnings_and_additional_checks_results = dict()

    # Do additional checks
    for name, url in ALLOWED_RECORD_TYPES.items():
        warnings_and_additional_checks_results.setdefault(name, list())
        warnings_and_additional_checks_results[name] = \
            do_additional_checks(json_to_test[name], url, name)
    return warnings_and_additional_checks_results


@app.task
def collect_relationships_issues(json_to_test):
    """
    This task will do relationships check
    :param json_to_test: json to be tested
    :return: all issues in dict
    """
    relationships = dict()
    biosamples_ids_to_call = set()
    # In first iteration need to collect all relationships
    for name, url in ALLOWED_RECORD_TYPES.items():
        new_relationships, biosample_ids = collect_relationships(
            json_to_test[name], name)
        relationships.update(new_relationships)
        biosamples_ids_to_call.update(biosample_ids)
    biosample_data = fetch_biosample_data_for_ids(biosamples_ids_to_call)
    relationships.update(biosample_data)
    return check_relationships(relationships)


@app.task
def join_validation_results(results):
    """
    This task will join results from previous two tasks
    :param results: list with results of previous two tasks
    :return: joined issues in dict
    """
    joined_results_object = JoinedResults(results)
    return joined_results_object.join_results()