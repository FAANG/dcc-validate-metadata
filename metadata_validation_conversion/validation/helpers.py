import requests
from metadata_validation_conversion.helpers import get_samples_json
from metadata_validation_conversion.constants import SKIP_PROPERTIES


def validate(data, schema):
    """
    This function will send data to elixir-validator and collect all errors
    :param data: data to validate in JSON format
    :param schema: schema to validate against
    :return: 'VALID' if everything is OK or error message
    """
    json_to_send = {
        'schema': schema,
        'object': data
    }
    response = requests.post(
        'http://localhost:3020/validate', json=json_to_send).json()
    if 'validationState' in response and response['validationState'] == 'VALID':
        return response['validationState']
    else:
        for error in response['validationErrors']:
            print(error['userFriendlyMessage'])
        return response['validationErrors']


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
    for record in records:
        core_warnings = check_item_is_present(record['samples_core'],
                                              recommended_core_fields)
        type_warnings = check_item_is_present(record, recommended_type_fields)
        if len(core_warnings) > 0:
            warnings_to_return.append(f"{name} records doesn't have these "
                                      f"recommended fields in core part: "
                                      f"{', '.join(core_warnings)}")
        if len(type_warnings) > 0:
            warnings_to_return.append(f"{name} records doesn't have these "
                                      f"recommended fields in main part: "
                                      f"{', '.join(type_warnings)}")
    return warnings_to_return
