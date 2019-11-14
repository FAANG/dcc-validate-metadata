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
    if 'sample_name' not in record and 'sample_descriptor' not in record:
        return f"{name}_{index + 1}"
    else:
        if 'sample_name' in record:
            return record['sample_name']['value']
        else:
            return record['sample_descriptor']['value']
