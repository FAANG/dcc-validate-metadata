import requests
from .constants import BASE_URL, ORGANISM_URL, SKIP_PROPERTIES


def get_samples_json(url):
    """
    This function will fetch json from url and then fetch core json from $ref
    :param url: url for type json fiel
    :return: type and core json
    """
    samples_type_json = requests.get(url).json()
    samples_core_ref = samples_type_json['properties']['samples_core']['$ref']
    samples_core_json = requests.get(f"{BASE_URL}{samples_core_ref}").json()
    return samples_type_json, samples_core_json


def parse_json(json_to_parse):
    """
    This function will parse json and return field names with positions
    :param json_to_parse: json file that should be parsed
    :return: dict with field_names as keys and field sub_names as values
    """
    required_fields = dict()
    for pr_property, value in json_to_parse['properties'].items():
        if pr_property not in SKIP_PROPERTIES and value['type'] == 'object':
            required_fields.setdefault(pr_property, [])
            for sc_property in value['required']:
                required_fields[pr_property].append(sc_property)
        elif pr_property not in SKIP_PROPERTIES and value['type'] == 'array':
            required_fields.setdefault(pr_property, [])
            for sc_property in value['items']['required']:
                required_fields[pr_property].append(sc_property)
    return required_fields


def get_field_names():
    """
    This function will create dict with field_names as keys and field sub_names
    as values
    :return dict with core and type field_names and indexes
    """
    organisms_type_json, organisms_core_json = get_samples_json(ORGANISM_URL)
    data_to_return = dict()
    data_to_return['core'] = parse_json(organisms_core_json)
    data_to_return['type'] = parse_json(organisms_type_json)
    return data_to_return


def get_samples_core_data(input_data, field_names_indexes):
    """
    This function will fetch information about core sample
    :param input_data: row from template to fetch information from
    :param field_names_indexes: dict with field names and indexes from json
    :return: dict with required information
    """
    samples_core = dict()
    for field_name, indexes in field_names_indexes.items():
        check_existence(field_name, samples_core,
                        get_data(input_data, **indexes))
    return samples_core


def get_organism_data(input_data, field_names_indexes):
    """
    This function will fetch information about organism
    :param input_data: row from template to fetch information from
    :param field_names_indexes: dict with field names and indexes from json
    :return: dict with required information
    """
    organism_to_validate = dict()
    organism_to_validate['samples_core'] = get_samples_core_data(
        input_data, field_names_indexes['core'])

    for field_name, indexes in field_names_indexes['type'].items():
        check_existence(field_name, organism_to_validate,
                        get_data(input_data, **indexes))

    # TODO add child_of, health_status and custom_data
    # get child_of
    # parent1 = get_data(input_data, **{'value': 10})
    # parent2 = get_data(input_data, **{'value': 11})
    # parents = list()
    # if parent1 is not None:
    #     parents.append(parent1)
    # if parent2 is not None:
    #     parents.append(parent2)
    # if len(parents) > 0:
    #     organism_to_validate['child_of'] = parents

    return organism_to_validate


def get_data(input_data, **fields):
    """
    This function will create dict with required fields and required information
    :param input_data: row from template
    :param fields: dict with field name as key and field index as value
    :return: dict with required information
    """
    data_to_return = dict()
    for field_name, field_index in fields.items():
        if input_data[field_index] == '':
            return None
        else:
            data_to_return[field_name] = input_data[field_index]
    return data_to_return


def check_existence(field_name, data_to_validate, template_data):
    """
    This function will check whether template_data has required field
    :param field_name: name of field
    :param data_to_validate: data dict for validation
    :param template_data: template data to check
    """
    if template_data is not None:
        data_to_validate[field_name] = template_data


def convert_to_snake_case(my_string):
    """
    This function will convert any string to camel_case string
    :param my_string: string to convert
    :return: string in camel_case format
    """
    return '_'.join(my_string.lower().split(" "))


def return_all_indexes(array_to_check, item_to_check):
    """
    This function will return array of all indexes of iterm in array
    :param array_to_check: array to look into
    :param item_to_check: item to search
    :return:
    """
    return [index for index, value in enumerate(array_to_check) if value ==
            item_to_check]

