import requests
import xlrd
from metadata_validation_conversion.constants import SAMPLE_CORE_URL, \
    SKIP_PROPERTIES, SPECIAL_PROPERTIES, JSON_TYPES


def get_samples_json(url):
    """
    This function will fetch json from url and then fetch core json from $ref
    :param url: url for type json fiel
    :return: type and core json
    """
    samples_type_json = requests.get(url).json()
    samples_core_json = requests.get(SAMPLE_CORE_URL).json()
    return samples_type_json, samples_core_json


def parse_json(json_to_parse):
    """
    This function will parse json and return field names with positions
    :param json_to_parse: json file that should be parsed
    :return: dict with field_names as keys and field sub_names as values
    """
    required_fields = dict()
    array_fields = list()
    for pr_property, value in json_to_parse['properties'].items():
        if pr_property not in SKIP_PROPERTIES and value['type'] == 'object':
            required_fields.setdefault(pr_property, [])
            for sc_property in value['required']:
                required_fields[pr_property].append(sc_property)
        elif pr_property not in SKIP_PROPERTIES and value['type'] == 'array':
            array_fields.append(pr_property)
            required_fields.setdefault(pr_property, [])
            for sc_property in value['items']['required']:
                required_fields[pr_property].append(sc_property)
    return required_fields, array_fields


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


def get_indices(field_name, field_types, headers, array_fields):
    """
    This function will return position of fields in template
    :param field_name: name of the field
    :param field_types: types that this field has
    :param headers: template header
    :param array_fields: list with names of fields that has array type
    :return: dict with positions of types of field
    """
    if field_name not in headers:
        print(f"Can't find this property: {field_name} in headers")
    if len(field_types) == 1 and 'value' in field_types:
        indices = return_all_indexes(headers, field_name)
        if len(indices) == 1 and field_name not in array_fields:
            return {'value': indices[0]}
        elif (len(indices) > 1 and field_name in array_fields) or \
                (field_name in array_fields):
            indices_list = list()
            for index in indices:
                indices_list.append({'value': index})
            return indices_list
        else:
            print(f"1. Template is broken for this field: {field_name}")
    else:
        if field_types == ['value', 'units']:
            value_indices = return_all_indexes(headers, field_name)
            if len(value_indices) == 1 and field_name not in array_fields:
                return check_field_existence(value_indices[0], headers,
                                             field_name, 'value', 'unit')
            elif (len(value_indices) > 1 and field_name in array_fields) or \
                    (field_name in array_fields):
                indices_list = list()
                for index in value_indices:
                    indices_list.append(check_field_existence(index, headers,
                                                              field_name,
                                                              'value', 'unit'))
                return indices_list
            else:
                print(f"2. Template is broken for this field: {field_name}")
        elif field_types == ['text', 'term']:
            text_indices = return_all_indexes(headers, field_name)
            if len(text_indices) == 1 and field_name not in array_fields:
                return check_field_existence(text_indices[0], headers,
                                             field_name, 'text',
                                             'term_source_id')
            elif (len(text_indices) > 1 and field_name in array_fields) or \
                    (field_name in array_fields):
                indices_list = list()
                for index in text_indices:
                    indices_list.append(check_field_existence(index, headers,
                                                              field_name,
                                                              'text',
                                                              'term_source_id'))
                return indices_list
            else:
                print(f"3. Template is broken for this field: {field_name}")
        else:
            print(f"4. Template is broken for this field types: {field_types}")


def get_custom_data_fields(headers, field_names):
    custom_data_fields_indexes = dict()
    array_fields = list()
    for header in headers:
        if header not in field_names['core'] and \
                header not in field_names['type'] and \
                header not in SPECIAL_PROPERTIES:
            indexes = return_all_indexes(headers, header)
            if len(indexes) > 1:
                array_fields.append(header)
            if headers[indexes[0] + 1] == 'unit':
                custom_data_fields_indexes[header] = ['value', 'units']
            elif headers[indexes[0] + 1] == 'term_source_id':
                custom_data_fields_indexes[header] = ['text', 'term']
            else:
                custom_data_fields_indexes[header] = ['value']
    return custom_data_fields_indexes, array_fields


def get_field_names_and_indexes(headers, url):
    """
    This function will create dict with field_names as keys and field sub_names
    with its indices inside template as values
    :return dict with core and type field_names and indexes
    """
    field_names = dict()
    array_fields = list()
    field_names_and_indexes = dict()
    samples_type_json, samples_core_json = get_samples_json(url)
    field_names['core'], tmp = parse_json(samples_core_json)
    array_fields.extend(tmp)
    field_names['type'], tmp = parse_json(samples_type_json)
    array_fields.extend(tmp)
    field_names['custom'], tmp = get_custom_data_fields(headers, field_names)
    array_fields.extend(tmp)

    for core_property, data_property in field_names.items():
        subtype_name_and_indexes = dict()
        for field_name, field_types in data_property.items():
            subtype_name_and_indexes[field_name] = get_indices(field_name,
                                                               field_types,
                                                               headers,
                                                               array_fields)
        field_names_and_indexes[core_property] = subtype_name_and_indexes
    return field_names_and_indexes


def get_data(input_data, date_field, wb_datemode, **fields):
    """
    This function will create dict with required fields and required information
    :param input_data: row from template
    :param date_field: boolean value is this data is date data
    :param wb_datemode: reference to datemode of current workbook
    :param fields: dict with field name as key and field index as value
    :return: dict with required information
    """
    data_to_return = dict()
    for field_name, field_index in fields.items():
        cell_value = input_data[field_index]
        if cell_value == '':
            return None
        else:
            # Convert all "_" in term ids to ":" as required by validator
            if field_name == 'term' and "_" in cell_value:
                cell_value = cell_value.replace("_", ":")

            # Convert date data to string (as Excel stores date in float format)
            if date_field is True and isinstance(cell_value, float):
                y, m, d, _, _, _ = xlrd.xldate_as_tuple(cell_value, wb_datemode)
                cell_value = f"{y}-{m}-{d}"
            data_to_return[field_name] = cell_value
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


def add_row(field_name, indexes, organism_to_validate, input_data, date_field,
            wb_datemode):
    if isinstance(indexes, list):
        tmp_list = list()
        for index in indexes:
            tmp_data = get_data(input_data, date_field, wb_datemode, **index)
            if tmp_data is not None:
                tmp_list.append(tmp_data)
        if len(tmp_list) != 0:
            organism_to_validate[field_name] = tmp_list
    else:
        check_existence(field_name, organism_to_validate,
                        get_data(input_data, date_field, wb_datemode,
                                 **indexes))


def check_cell_is_date(field_name):
    """
    This function will check that current column is date field
    :param field_name: name of column
    :return: True if column is date and False otherwise
    """
    if 'date' in field_name:
        return True
    else:
        return False


def get_sample_data(input_data, field_names_indexes, wb_datemode):
    """
    This function will fetch information about organism
    :param input_data: row from template to fetch information from
    :param field_names_indexes: dict with field names and indexes from json
    :param wb_datemode: reference to datemode of current workbook
    :return: dict with required information
    """
    organism_to_validate = dict()
    for k, v in JSON_TYPES.items():
        if v is not None:
            organism_to_validate.setdefault(v, dict())
            for field_name, indexes in field_names_indexes[k].items():
                date_field = check_cell_is_date(field_name)
                add_row(field_name, indexes, organism_to_validate[v],
                        input_data, date_field, wb_datemode)
        else:
            for field_name, indexes in field_names_indexes[k].items():
                date_field = check_cell_is_date(field_name)
                add_row(field_name, indexes, organism_to_validate, input_data,
                        date_field, wb_datemode)
    return organism_to_validate


def convert_to_snake_case(my_string):
    """
    This function will convert any string to camel_case string
    :param my_string: string to convert
    :return: string in camel_case format
    """
    return '_'.join(my_string.lower().split(" "))

