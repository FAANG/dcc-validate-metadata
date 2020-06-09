import requests
from metadata_validation_conversion.constants import ELIXIR_VALIDATOR_URL
import json


def sanitize(data: dict, sanitize_map: dict):
    """
    Elixir validator treats field name containing '-' or ':' as multiple value field even they are not
    This method change - and : to _ to avoid this happen
    :param data: the data before sanitization
    :param sanitize_map: the map between sanitized field name and the original field name
    :return: sanitized data
    """
    result = data
    for sanitized_value, to_be_processed in sanitize_map.items():
        result[sanitized_value] = result.pop(to_be_processed)
    return result


def unsanitize_error(error: dict, sanitized_map: dict):
    """
    The sanitized field name would not match to the field name in the template, then raise error
    Manually update the error value to match to the template
    :param error: the error object returned by the Elixir validator
    :param sanitized_map: the map between sanitized name (keys) and original name used in the template (values)
    :return: curated error
    """
    # no sanitized columns
    if len(sanitized_map) == 0:
        return error
    # sanitization is to prevent validator wrongly treat single value column as multiple value column,
    # hence safe to skip checking for [], field name should always be after the first .
    paths = error['absoluteDataPath'].split('.')
    if paths[1] in sanitized_map:
        paths[1] = sanitized_map[paths[1]]
        error['absoluteDataPath'] = ".".join(paths)
        error['userFriendlyMessage'] = f"{error['message']} at {error['absoluteDataPath']}"
    return error


def validate(data, schema):
    """
    This function will send data to elixir-validator and collect all errors
    :param data: data to validate in JSON format
    :param schema: schema to validate against
    :return: list of error messages
    """
    sanitized_map = dict()
    for field_name in data.keys():
        sanitized_name = field_name.replace('-', '_')
        sanitized_name = sanitized_name.replace(':', '_')
        if sanitized_name != field_name:
            sanitized_map[sanitized_name] = field_name

    sanitized_data = sanitize(data, sanitized_map)
    sanitized_schema = schema
    sanitized_schema['properties'] = sanitize(schema['properties'], sanitized_map)

    json_to_send = {
        'schema': sanitized_schema,
        'object': sanitized_data
    }
    response = requests.post(ELIXIR_VALIDATOR_URL, json=json_to_send).json()
    validation_errors = list()
    paths = list()

    # example response
    # "validationErrors": [{"ajvError": {some data}, "message": "should be number",
    # "absoluteDataPath": ".rna_purity_260_230_ratio.value",
    # "userFriendlyMessage": "should be number at .rna_purity_260_230_ratio.value"},{another error}]
    # the abosluteDataPath should be reverted back to the name used in the template .rna_purity-260:280_ratio.value
    if 'validationErrors' in response and len(
            response['validationErrors']) > 0:
        for error in response['validationErrors']:
            unsanitized_error = unsanitize_error(error, sanitized_map)
            validation_errors.append(unsanitized_error['userFriendlyMessage'])
            paths.append(unsanitized_error['absoluteDataPath'])
    return validation_errors, paths


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
            return f"{record['custom']['sample_descriptor']['value']}-" \
                   f"{record['custom']['experiment_alias']['value']}"
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
            if check_issues(record):
                return 'Fix issues'
    return 'Ready for submission'


def check_issues(record):
    """
    This function will return True if any issues exist
    :param record: record to check
    :return: True if any issues and False otherwise
    """
    for key, value in record.items():
        if isinstance(value, list):
            for item in value:
                if 'errors' in item and len(item['errors']) > 0:
                    return True
        elif key in ['samples_core', 'custom', 'experiments_core', 'module']:
            for k, v in value.items():
                if 'errors' in v and len(v['errors']) > 0:
                    return True
        else:
            if 'errors' in value and len(value['errors']) > 0:
                return True
    return False


def get_record_structure(structure, record, module_name=None):
    """
    this function will create structure to return to front-end
    :param structure: structure of a table
    :param record: record that came from table
    :param module_name: name of the module_field
    :return: structure to return to front-end
    """
    results = parse_data(structure['type'], record)
    if 'samples_core' in record:
        results['samples_core'] = parse_data(structure['core'],
                                             record['samples_core'])
    elif 'experiments_core' in record:
        results['experiments_core'] = parse_data(structure['core'],
                                                 record['experiments_core'])
    results['custom'] = parse_data(structure['custom'], record['custom'])
    if 'module' in structure and module_name is not None:
        results[module_name] = parse_data(structure['module'], record[module_name])
    return results


def parse_data(structure, record):
    """
    This function will copy data from record to structure
    :param structure: structure of a table
    :param record: record that came from table
    :return: converted data
    """
    results = dict()
    for k, v in structure.items():
        if isinstance(v, dict):
            if k in record:
                results[k] = convert_to_none(v, record[k])
            else:
                results[k] = convert_to_none(v)
        else:
            for index, value in enumerate(v):
                results.setdefault(k, list())
                if k in record and index < len(record[k]):
                    results[k].append(convert_to_none(value, record[k][index]))
                else:
                    results[k].append(convert_to_none(value))
    return results


def convert_to_none(structure, data_to_check=None):
    """
    This function will assign fields to None
    :param data_to_check: data to check values
    :param structure: dict to parse
    :return: dict with None for fields
    """
    results = dict()
    if data_to_check is None:
        for k in structure:
            results[k] = None
    else:
        for k in structure:
            if k in data_to_check:
                results[k] = data_to_check[k]
            else:
                results[k] = None
    return results
