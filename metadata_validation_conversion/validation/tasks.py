from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from .ElixirValidatorResults import ElixirValidatorResults
from .JoinedResults import JoinedResults
from .RelationshipsIssues import RelationshipsIssues
from .WarningsAndAdditionalChecks import WarningsAndAdditionalChecks


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
    additional_checks_object = WarningsAndAdditionalChecks(json_to_test)
    return additional_checks_object.collect_warnings_and_additional_checks()


@app.task
def collect_relationships_issues(json_to_test):
    """
    This task will do relationships check
    :param json_to_test: json to be tested
    :return: all issues in dict
    """
    relationships_issues_object = RelationshipsIssues(json_to_test)
    return relationships_issues_object.collect_relationships_issues()


@app.task
def join_validation_results(results):
    """
    This task will join results from previous two tasks
    :param results: list with results of previous two tasks
    :return: joined issues in dict
    """
    joined_results_object = JoinedResults(results)
    results = joined_results_object.join_results()
    send_message(status='Success', validation_results=results);
    return 'Success'
