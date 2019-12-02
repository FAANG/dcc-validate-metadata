import requests
from metadata_validation_conversion.constants import ELIXIR_VALIDATOR_URL


def validate(data, schema):
    """
    This function will send data to elixir-validator and collect all errors
    :param data: data to validate in JSON format
    :param schema: schema to validate against
    :return: list of error messages
    """
    json_to_send = {
        'schema': schema,
        'object': data
    }
    response = requests.post(ELIXIR_VALIDATOR_URL, json=json_to_send).json()
    validation_errors = list()
    if 'validationErrors' in response and len(
            response['validationErrors']) > 0:
        for error in response['validationErrors']:
            validation_errors.append(error['userFriendlyMessage'])
    return validation_errors


def get_validation_results_structure(record_name, include_module=False):
    """
    This function will create inner validation results structure
    :param record_name: name of the record
    :param include_module: include module field or not
    :return: inner validation results structure
    """
    structure_to_return = {
        "name": record_name,
        "core": {
            "errors": list(),
            "warnings": list()
        },
        "type": {
            "errors": list(),
            "warnings": list()
        },
        "custom": {
            "errors": list(),
            "warnings": list()
        }
    }
    if include_module:
        structure_to_return.update(
            {"module": {"errors": list(), "warnings": list()}})
    return structure_to_return


def get_record_name(record, index, name):
    """
    This function will return name of the current record or create it
    :param record: record to search name in
    :param index: index for new name creation
    :param name: name of the record
    :return: name of the record
    """
    if 'sample_name' not in record['custom'] \
            and 'sample_descriptor' not in record['custom'] \
            and 'alias' not in record:
        return f"{name}_{index + 1}"
    else:
        if 'sample_name' in record['custom']:
            return record['custom']['sample_name']['value']
        elif 'sample_descriptor' in record['custom']:
            return record['custom']['sample_descriptor']['value']
        else:
            return record['alias']['value']


def get_submission_status(validation_results):
    """
    This function will check results for error and return appropriate message
    :param validation_results: json to check
    :return: submission status
    """
    for _, v in validation_results.items():
        for record in v:
            if check_issues(record, 'core') or check_issues(record, 'type') \
                    or check_issues(record, 'custom') \
                    or check_issues(record, 'module'):
                return 'Fix issues'
    return 'Ready for submission'


def check_issues(record, issue_type):
    """
    This function will return True if any issues exist
    :param record: record to check
    :param issue_type: type of issues to check
    :return: True if any issues and False otherwise
    """
    if issue_type in record:
        return len(record[issue_type]['errors']) > 0
    else:
        return False
