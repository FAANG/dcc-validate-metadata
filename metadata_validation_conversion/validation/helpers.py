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
    paths = list()
    if 'validationErrors' in response and len(
            response['validationErrors']) > 0:
        for error in response['validationErrors']:
            validation_errors.append(error['userFriendlyMessage'])
            paths.append(error['absoluteDataPath'])
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


def get_record_structure(structure, record):
    """
    this function will create structure to return to front-end
    :param structure: structure of a table
    :param record: record that came from table
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
    if 'module' in structure:
        results['module'] = parse_data(structure['module'], record['module'])
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
                results[k] = record[k].copy()
            else:
                results[k] = convert_to_none(v)
        else:
            for index, value in enumerate(v):
                results.setdefault(k, list())
                try:
                    results[k].append(record[k][index].copy())
                except (IndexError, KeyError):
                    results[k].append(convert_to_none(value))
    return results


def convert_to_none(dict_to_convert):
    """
    This function will assign fields to None
    :param dict_to_convert: dict to parse
    :return: dict with None for fields
    """
    results = dict()
    for k in dict_to_convert:
        results[k] = None
    return results
