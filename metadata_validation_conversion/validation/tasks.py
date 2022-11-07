from abc import ABC

from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from .ElixirValidatorResults import ElixirValidatorResults
from .JoinedResults import JoinedResults
from .RelationshipsIssues import RelationshipsIssues
from .WarningsAndAdditionalChecks import WarningsAndAdditionalChecks
from .helpers import get_submission_status

from celery import Task


class LogErrorsTask(Task, ABC):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        send_message(room_id=kwargs['room_id'], validation_status='Error',
                     errors=f'There is a problem with the validation process. Error: {exc}')


@app.task(base=LogErrorsTask)
def validate_against_schema(json_to_test, rules_type, structure, room_id):
    """
    Task to send json data to elixir-validator
    :param json_to_test: json to test against schema
    :param rules_type: type of rules to validate
    :param structure: structure of original template
    :return: all issues in dict
    """
    elixir_validation_results = ElixirValidatorResults(json_to_test,
                                                       rules_type,
                                                       structure)
    return elixir_validation_results.run_validation()


@app.task(base=LogErrorsTask)
def collect_warnings_and_additional_checks(json_to_test, rules_type,
                                           structure, room_id):
    """
    Task to do additional checks inside python app
    :param json_to_test: json to test against additional checks
    :param rules_type: type of rules to validate
    :param structure: structure of original template
    :return: all issues in dict
    """
    additional_checks_object = WarningsAndAdditionalChecks(json_to_test,
                                                           rules_type,
                                                           structure)
    return additional_checks_object.collect_warnings_and_additional_checks()


@app.task(base=LogErrorsTask)
def collect_relationships_issues(json_to_test, validation_type, structure, room_id):
    """
    This task will do relationships check
    :param json_to_test: json to be tested
    :param structure: structure of original template
    :return: all issues in dict
    """
    relationships_issues_object = RelationshipsIssues(json_to_test, validation_type, structure)
    return relationships_issues_object.collect_relationships_issues()


@app.task(base=LogErrorsTask)
def join_validation_results(results, room_id):
    """
    This task will join results from previous two tasks
    :param room_id: room id to create ws url
    :param results: list with results of previous two tasks
    :return: joined issues in dict
    """
    joined_results_object = JoinedResults(results)
    results = joined_results_object.join_results()
    submission_status = get_submission_status(results)
    send_message(validation_status='Finished', room_id=room_id,
                 table_data=results, submission_status=submission_status)
    return results

