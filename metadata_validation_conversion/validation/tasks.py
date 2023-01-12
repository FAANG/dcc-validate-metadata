from abc import ABC

from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from .ElixirValidatorResults import ElixirValidatorResults
from .JoinedResults import JoinedResults
from .RelationshipsIssues import RelationshipsIssues
from .WarningsAndAdditionalChecks import WarningsAndAdditionalChecks
from .helpers import get_submission_status

from celery import Task
from metadata_validation_conversion.constants import SAMPLES_ALLOWED_SPECIAL_SHEET_NAMES
from .update_utils import check_biosampleid



class LogErrorsTask(Task, ABC):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        send_message(room_id=kwargs['room_id'], validation_status='Error',
                     errors=f'There is a problem with the validation process. Error: {exc}')


@app.task(base=LogErrorsTask)
def verify_sample_ids(json_to_test, room_id):
    """
    This task verifies the biosample id provided for the update process
    :param room_id: room id to create ws url
    :param json_to_test: dictionary containing submitted worksheet data
    :return: valid and invalid sample ids
    """
    erroneous_sample_ids = list()
    reg_valid_sample_ids = list()
    for sheetname, submitted_data in json_to_test.items():
        if sheetname not in SAMPLES_ALLOWED_SPECIAL_SHEET_NAMES:
            for ele in submitted_data:
                # check biosample_id of entry
                try:
                    sample_id = ele['custom']['biosample_id']['value']
                    reg_valid_sample_ids, erroneous_sample_ids = check_biosampleid(sample_id.upper(),
                                                                                   reg_valid_sample_ids,
                                                                                   erroneous_sample_ids)
                except KeyError:
                    send_message(validation_status='Error', room_id=room_id,
                                 errors=f'There is a problem with the validation process. '
                                        f'sample_id missing in sheet {sheetname}')
                    return

                # check biosample_id of derived_from
                # derived_from is not a mandatory field, pass if key is missing
                try:
                    derived_from = ele['derived_from']

                    if isinstance(derived_from, list):
                        for entry in derived_from:
                            reg_valid_sample_ids, erroneous_sample_ids = check_biosampleid(entry['value'].upper(),
                                                                                           reg_valid_sample_ids,
                                                                                           erroneous_sample_ids)
                    if isinstance(derived_from, dict):
                        reg_valid_sample_ids, erroneous_sample_ids = check_biosampleid(derived_from['value'].upper(),
                                                                                       reg_valid_sample_ids,
                                                                                       erroneous_sample_ids)
                except KeyError:
                    pass

    return reg_valid_sample_ids, erroneous_sample_ids


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
def collect_relationships_issues(json_to_test, validation_type, structure, action, room_id):
    """
    This task will do relationships check
    :param json_to_test: json to be tested
    :param structure: structure of original template
    :return: all issues in dict
    """
    relationships_issues_object = RelationshipsIssues(json_to_test, validation_type, structure, action)
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

