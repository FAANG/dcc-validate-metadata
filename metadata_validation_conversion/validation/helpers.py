import requests
from metadata_validation_conversion.helpers import get_samples_json
from metadata_validation_conversion.constants import SKIP_PROPERTIES


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
    response = requests.post(
        'http://localhost:3020/validate', json=json_to_send).json()
    validation_errors = list()
    if 'validationErrors' in response and len(response['validationErrors']) > 0:
        for error in response['validationErrors']:
            validation_errors.append(error['userFriendlyMessage'])
    return validation_errors


def collect_recommended_fields(json_to_check):
    """
    This function will return list of recommended fields
    :param json_to_check: json to check for recommended fields
    :return: list with recommended fields
    """
    recommended_fields = list()
    for field_name, field_value in json_to_check['properties'].items():
        if field_name not in SKIP_PROPERTIES:
            if field_value['type'] == 'object':
                if field_value['properties']['mandatory']['const'] == \
                        'recommended':
                    recommended_fields.append(field_name)
            elif field_value['type'] == 'array':
                if field_value['items']['properties']['mandatory']['const'] == \
                        'recommended':
                    recommended_fields.append(field_name)
    return recommended_fields


def check_item_is_present(dict_to_check, list_of_items):
    warnings = list()
    for item in list_of_items:
        if item not in dict_to_check:
            warnings.append(item)
    return warnings


def check_recommended_fields_are_present(records, url, name):
    """
    This function will return warning if recommended fields is not present in
    record
    :param records: record to check
    :param url: schema url for this record
    :param name: name of the item to check
    :return: warnings
    """
    warnings_to_return = list()
    samples_type_json, samples_core_json = get_samples_json(url)
    recommended_type_fields = collect_recommended_fields(samples_type_json)
    recommended_core_fields = collect_recommended_fields(samples_core_json)
    for index, record in enumerate(records):
        record_name = get_record_name(record['custom'], index)
        tmp = get_validation_results_structure(record_name)
        core_warnings = check_item_is_present(record['samples_core'],
                                              recommended_core_fields)
        type_warnings = check_item_is_present(record, recommended_type_fields)
        if len(core_warnings) > 0:
            tmp['core']['warnings'].append(f"{name} records doesn't have these "
                                           f"recommended fields in core part: "
                                           f"{', '.join(core_warnings)}")
        if len(type_warnings) > 0:
            tmp['type']['warnings'].append(f"{name} records doesn't have these "
                                           f"recommended fields in main part: "
                                           f"{', '.join(type_warnings)}")
        warnings_to_return.append(tmp)
    return warnings_to_return


def get_validation_results_structure(record_name):
    """
    This function will create inner validation results structure
    :param record_name: name of the record
    :return: inner validation results structure
    """
    return {
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


def get_record_name(record, index):
    """
    This function will return name of the current record or create it
    :param record: record to search name in
    :param index: index for new name creation
    :return: name of the record
    """
    if 'sample_name' not in record:
        return f"record_{index + 1}"
    else:
        return record['sample_name']['value']
