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


def return_all_indexes(array_to_check, item_to_check):
    """
    This function will return array of all indexes of iterm in array
    :param array_to_check: array to look into
    :param item_to_check: item to search
    :return:
    """
    return [index for index, value in enumerate(array_to_check) if value ==
            item_to_check]


def check_field_existence(index, headers, field, first_subfield,
                          second_subfield):
    """
    This function will check whether table has all required fields
    :param index: index to check in table
    :param headers: list with header names
    :param field: field name
    :param first_subfield: first subfield name
    :param second_subfield: second subfield name
    :return: dict with subfield indexes
    """
    if headers[index + 1] != second_subfield:
        print(f"This property {field} doesn't have {second_subfield} provided "
              f"in template!")
    else:
        if second_subfield == 'unit':
            second_subfield = 'units'
        elif second_subfield == 'term_source_id':
            second_subfield = 'term'
        return {first_subfield: index, second_subfield: index + 1}


def get_indices(field_name, field_types, headers):
    """
    This function will return position of fields in template
    :param field_name: name of the field
    :param field_types: types that this field has
    :param headers: template header
    :return: dict with positions of types of field
    """
    if field_name not in headers:
        print(f"Can't find this property: {field_name} in headers")
    if len(field_types) == 1 and 'value' in field_types:
        indices = return_all_indexes(headers, field_name)
        if len(indices) == 1:
            return {'value': indices[0]}
        else:
            indices_list = list()
            for index in indices:
                indices_list.append({'value': index})
            return indices_list
    else:
        if field_types == ['value', 'units']:
            value_indices = return_all_indexes(headers, field_name)
            if len(value_indices) == 1:
                return check_field_existence(value_indices[0], headers,
                                             field_name, 'value', 'unit')
            else:
                indices_list = list()
                for index in value_indices:
                    indices_list.append(check_field_existence(index, headers,
                                                              field_name,
                                                              'value', 'unit'))
                return indices_list
        elif field_types == ['text', 'term']:
            text_indices = return_all_indexes(headers, field_name)
            if len(text_indices) == 1:
                return check_field_existence(text_indices[0], headers,
                                             field_name, 'text',
                                             'term_source_id')
            else:
                indices_list = list()
                for index in text_indices:
                    indices_list.append(check_field_existence(index, headers,
                                                              field_name,
                                                              'text',
                                                              'term_source_id'))
                return indices_list
        else:
            print("Template is broken!")


def get_field_names_and_indexes(headers):
    """
    This function will create dict with field_names as keys and field sub_names
    with its indices inside template as values
    :return dict with core and type field_names and indexes
    """
    field_names = dict()
    field_names_and_indexes = dict()
    organisms_type_json, organisms_core_json = get_samples_json(ORGANISM_URL)
    field_names['core'] = parse_json(organisms_core_json)
    field_names['type'] = parse_json(organisms_type_json)

    for core_property, data_property in field_names.items():
        subtype_name_and_indexes = dict()
        for field_name, field_types in data_property.items():
            subtype_name_and_indexes[field_name] = get_indices(field_name,
                                                               field_types,
                                                               headers)
        field_names_and_indexes[core_property] = subtype_name_and_indexes
    return field_names_and_indexes


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
        if isinstance(indexes, list):
            tmp_list = list()
            for index in indexes:
                tmp_data = get_data(input_data, **index)
                if tmp_data is not None:
                    tmp_list.append(tmp_data)
            if len(tmp_list) != 0:
                organism_to_validate[field_name] = tmp_list
        else:
            check_existence(field_name, organism_to_validate,
                            get_data(input_data, **indexes))
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

