import requests
from .constants import BASE_URL, ORGANISM_URL


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


def parse_json(json_to_parse, template_index, data_to_return):
    """
    This function will parse json and return field names with positions
    :param json_to_parse: json file that should be parsed
    :param template_index: index in template
    :param data_to_return: results
    :return: index in template when it stops
    """
    for index, value in enumerate(json_to_parse['properties'].items()):
        if 'properties' in value[1]:
            if template_index == 0:
                template_index = index - 2
            for name in value[1]['required']:
                template_index += 1
                data_to_return.setdefault(value[0], {})
                data_to_return[value[0]][name] = template_index
    return template_index


def get_field_names_indexes():
    """
    This function will create dict with field_names as keys and field sub_names
    with template indexes as value
    """
    organisms_type_json, organisms_core_json = get_samples_json(ORGANISM_URL)
    template_index = 0
    data_to_return = dict()
    template_index = parse_json(organisms_core_json, template_index,
                                data_to_return)
    _ = parse_json(organisms_type_json, template_index, data_to_return)
    for k, v in data_to_return.items():
        print(f"{k}\t{v}")

