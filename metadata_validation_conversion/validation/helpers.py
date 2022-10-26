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
    for item in response:
        validation_errors.append(', '.join(item['errors']))
        paths.append(item['dataPath'])
    return validation_errors, paths


def get_record_name(record, index, name, action):
    """
    This function will return name of the current record or create it
    :param record: record to search name in
    :param index: index for new name creation
    :param name: name of the record
    :param action: indicates whether it's a new submission or update
    :return: name of the record
    """
    primary_col_name = 'sample_name'
    if action == 'update':
        primary_col_name = 'biosample_id'

    if primary_col_name not in record['custom'] \
            and 'sample_descriptor' not in record['custom'] \
            and 'alias' not in record:
        return f"{name}_{index + 1}"
    else:
        if primary_col_name in record['custom']:
            return record['custom'][primary_col_name]['value']
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
        if key in ['samples_core', 'custom', 'experiments_core',
                   'input_dna', 'dna-binding_proteins', 'teleostei_embryo',
                   'teleostei_post-hatching']:
            if check_issues(value):
                return True
        if isinstance(value, list):
            for item in value:
                if 'errors' in item and len(item['errors']) > 0:
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
