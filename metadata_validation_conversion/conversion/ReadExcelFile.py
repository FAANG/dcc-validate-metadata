import xlrd
from metadata_validation_conversion.constants import ALLOWED_SHEET_NAMES, \
    SKIP_PROPERTIES, SPECIAL_PROPERTIES, JSON_TYPES, CHIP_SEQ_INPUT_DNA_URL, \
    CHIP_SEQ_DNA_BINDING_PROTEINS_URL
from metadata_validation_conversion.helpers import convert_to_snake_case, \
    get_rules_json


class ReadExcelFile:
    def __init__(self, file_path, json_type):
        self.file_path = file_path
        self.json_type = json_type
        self.headers = list()
        self.array_fields = list()
        self.wb_datemode = None

    def start_conversion(self):
        """
        Main function that will convert xlsx file to proper json format
        :return: submitted data in proper json format
        """
        wb = xlrd.open_workbook(self.file_path)
        self.wb_datemode = wb.datemode
        data = dict()
        for sh in wb.sheets():
            if sh.name not in ALLOWED_SHEET_NAMES:
                if sh.name == 'faang_field_values':
                    continue
                return f"Error: there are no rules for {sh.name} type!"
            else:
                tmp = list()
                self.headers = [
                    convert_to_snake_case(item) for item in sh.row_values(0)]
                try:
                    field_names_indexes = self.get_field_names_and_indexes(
                        sh.name)
                except ValueError as err:
                    return err.args[0]
                for row_number in range(1, sh.nrows):
                    sample_data = self.get_sample_data(
                        sh.row_values(row_number), field_names_indexes)
                    material_consistency = \
                        self.check_sheet_name_material_consistency(sample_data,
                                                                   sh.name)
                    if material_consistency is not False:
                        return material_consistency
                    tmp.append(sample_data)
                data[convert_to_snake_case(sh.name)] = tmp
        return data

    def get_field_names_and_indexes(self, sheet_name):
        """
        This function will create dict with field_names as keys and field
        sub_names
        with its indices inside template as values
        :return dict with core and type field_names and indexes
        """
        field_names = dict()
        array_fields = list()
        field_names_and_indexes = dict()

        url = ALLOWED_SHEET_NAMES[sheet_name]
        if sheet_name == 'chip-seq input dna':
            type_json, core_json, module_json = get_rules_json(
                url, self.json_type, CHIP_SEQ_INPUT_DNA_URL)
            field_names['module'], tmp = self.parse_json(module_json)
            array_fields.extend(tmp)
        elif sheet_name == 'chip-seq dna-binding proteins':
            type_json, core_json, module_json = get_rules_json(
                url, self.json_type, CHIP_SEQ_DNA_BINDING_PROTEINS_URL)
            field_names['module'], tmp = self.parse_json(module_json)
            array_fields.extend(tmp)
        else:
            type_json, core_json = get_rules_json(url, self.json_type)
        field_names['core'], tmp = self.parse_json(core_json)
        array_fields.extend(tmp)
        field_names['type'], tmp = self.parse_json(type_json)
        array_fields.extend(tmp)
        field_names['custom'], tmp = self.get_custom_data_fields(field_names)
        array_fields.extend(tmp)

        for core_property, data_property in field_names.items():
            subtype_name_and_indexes = dict()
            for field_name, field_types in data_property.items():
                subtype_name_and_indexes[field_name] = self.get_indices(
                    field_name, field_types, array_fields)
            field_names_and_indexes[core_property] = subtype_name_and_indexes
        return field_names_and_indexes

    @staticmethod
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
            elif pr_property not in SKIP_PROPERTIES and \
                    value['type'] == 'array':
                array_fields.append(pr_property)
                required_fields.setdefault(pr_property, [])
                for sc_property in value['items']['required']:
                    required_fields[pr_property].append(sc_property)
        return required_fields, array_fields

    def get_custom_data_fields(self, field_names):
        """
        This function will go through headers and find all remaining names that
        are not in field_names
        :param field_names: names from json-schema
        :return: rules for custom fields in dict and all array fields
        """
        custom_data_fields_indexes = dict()
        array_fields = list()
        for header in self.headers:
            if header not in field_names['core'] and \
                    header not in field_names['type'] and \
                    header not in SPECIAL_PROPERTIES:
                indexes = self.return_all_indexes(header)
                if len(indexes) > 1:
                    array_fields.append(header)
                if len(self.headers)-1 > (indexes[0] + 1) and \
                        self.headers[indexes[0] + 1] == 'unit':
                    custom_data_fields_indexes[header] = ['value', 'units']
                elif len(self.headers)-1 > (indexes[0] + 1) and \
                        self.headers[indexes[0] + 1] == 'term_source_id':
                    custom_data_fields_indexes[header] = ['text', 'term']
                else:
                    custom_data_fields_indexes[header] = ['value']
        return custom_data_fields_indexes, array_fields

    def return_all_indexes(self, item_to_check):
        """
        This function will return array of all indexes of iterm in array
        :param item_to_check: item to search
        :return:
        """
        return [index for index, value in enumerate(self.headers) if value ==
                item_to_check]

    def get_indices(self, field_name, field_types, array_fields):
        """
        This function will return position of fields in template
        :param field_name: name of the field
        :param field_types: types that this field has
        :param array_fields
        :return: dict with positions of types of field
        """
        if field_name not in self.headers:
            raise ValueError(
                f"Error: can't find this property '{field_name}' in "
                f"headers")
        if len(field_types) == 1 and 'value' in field_types:
            indices = self.return_all_indexes(field_name)
            if len(indices) == 1 and field_name not in array_fields:
                return {'value': indices[0]}
            elif (len(indices) > 1 and field_name in array_fields) or \
                    (field_name in array_fields):
                indices_list = list()
                for index in indices:
                    indices_list.append({'value': index})
                return indices_list
            else:
                raise ValueError(f"Error: multiple entries for attribute "
                                 f"'{field_name}' present")
        else:
            if field_types == ['value', 'units']:
                value_indices = self.return_all_indexes(field_name)
                if len(value_indices) == 1 and field_name not in array_fields:
                    return self.check_field_existence(value_indices[0],
                                                      field_name, 'value',
                                                      'unit')
                elif (len(value_indices) > 1 and field_name in array_fields) \
                        or (field_name in array_fields):
                    indices_list = list()
                    for index in value_indices:
                        indices_list.append(
                            self.check_field_existence(index, field_name,
                                                       'value', 'unit'))
                    return indices_list
                else:
                    raise ValueError(f"Error: multiple entries for attribute "
                                     f"'{field_name}' present")
            elif field_types == ['text', 'term']:
                text_indices = self.return_all_indexes(field_name)
                if len(text_indices) == 1 and field_name not in array_fields:
                    return self.check_field_existence(text_indices[0],
                                                      field_name, 'text',
                                                      'term_source_id')
                elif (len(text_indices) > 1 and field_name in array_fields) \
                        or (field_name in array_fields):
                    indices_list = list()
                    for index in text_indices:
                        indices_list.append(
                            self.check_field_existence(index, field_name,
                                                       'text',
                                                       'term_source_id'))
                    return indices_list
                else:
                    raise ValueError(f"Error: multiple entries for attribute "
                                     f"'{field_name}' present")
            else:
                raise ValueError(f"Error: unknown types present for attribute "
                                 f"'{field_types}' present")

    def check_field_existence(self, index, field, first_subfield,
                              second_subfield):
        """
        This function will check whether table has all required fields
        :param index: index to check in table
        :param field: field name
        :param first_subfield: first subfield name
        :param second_subfield: second subfield name
        :return: dict with subfield indexes
        """
        if self.headers[index + 1] != second_subfield:
            raise ValueError(
                f"Error: this property {field} doesn't have {second_subfield} "
                f"provided in template!")
        else:
            if second_subfield == 'unit':
                second_subfield = 'units'
            elif second_subfield == 'term_source_id':
                second_subfield = 'term'
            return {first_subfield: index, second_subfield: index + 1}

    def get_sample_data(self, input_data, field_names_indexes):
        """
        This function will fetch information about organism
        :param input_data: row from template to fetch information from
        :param field_names_indexes: dict with field names and indexes from json
        :return: dict with required information
        """
        organism_to_validate = dict()
        for k, v in JSON_TYPES.items():
            if v is not None:
                organism_to_validate.setdefault(v, dict())
                for field_name, indexes in field_names_indexes[k].items():
                    date_field = self.check_cell_is_date(field_name)
                    self.add_row(field_name, indexes, organism_to_validate[v],
                                 input_data, date_field)
            else:
                for field_name, indexes in field_names_indexes[k].items():
                    date_field = self.check_cell_is_date(field_name)
                    self.add_row(field_name, indexes, organism_to_validate,
                                 input_data, date_field)
        return organism_to_validate

    @staticmethod
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

    def add_row(self, field_name, indexes, organism_to_validate, input_data,
                date_field):
        """
        High-level function to get data from table
        :param field_name: name of the field to add
        :param indexes: subfields of this field
        :param organism_to_validate: results holder
        :param input_data: row from table
        :param date_field: date field to check
        """
        if isinstance(indexes, list):
            tmp_list = list()
            for index in indexes:
                tmp_data = self.get_data(input_data, date_field, **index)
                if len(tmp_data) != 0:
                    tmp_list.append(tmp_data)
            if len(tmp_list) != 0:
                organism_to_validate[field_name] = tmp_list
        else:
            self.check_existence(field_name, organism_to_validate,
                                 self.get_data(input_data, date_field,
                                               **indexes))

    def get_data(self, input_data, date_field, **fields):
        """
        This function will create dict with required fields and required
        information
        :param input_data: row from template
        :param date_field: boolean value is this data is date data
        :param fields: dict with field name as key and field index as value
        :return: dict with required information
        """
        data_to_return = dict()
        for field_name, field_index in fields.items():
            cell_value = input_data[field_index]
            if cell_value != '':
                # Convert all "_" in term ids to ":" as required by validator
                if field_name == 'term' and "_" in cell_value:
                    cell_value = cell_value.replace("_", ":")

                # Convert date data to string (as Excel stores date in float
                # format)
                if date_field is True and isinstance(cell_value, float):
                    y, m, d, _, _, _ = xlrd.xldate_as_tuple(cell_value,
                                                            self.wb_datemode)
                    m = self.add_leading_zero(m)
                    d = self.add_leading_zero(d)
                    cell_value = f"{y}-{m}-{d}"
                data_to_return[field_name] = cell_value
        return data_to_return

    @staticmethod
    def check_existence(field_name, data_to_validate, template_data):
        """
        This function will check whether template_data has required field
        :param field_name: name of field
        :param data_to_validate: data dict for validation
        :param template_data: template data to check
        """
        if len(template_data) != 0:
            data_to_validate[field_name] = template_data

    @staticmethod
    def add_leading_zero(date_item):
        """
        This function will add leading zero if date is just one number
        :param date_item: item to check
        :return: date item in proper format (01, 02, etc...)
        """
        if date_item < 10:
            return f"0{date_item}"
        else:
            return date_item

    def check_sheet_name_material_consistency(self, sample_data, name):
        """
        This function checks that sheet has consistent material
        :param sample_data: data to check
        :param name: name of sheet
        :return: False or error
        """
        if self.json_type != 'samples':
            return False
        if 'samples_core' in sample_data and 'material' in \
                sample_data['samples_core'] and 'text' in \
                sample_data['samples_core']['material']:
            material = sample_data['samples_core']['material']['text']
            if material != name:
                return f"Error: '{name}' sheet contains record with " \
                       f"inconsistent material '{material}'"
            else:
                return False
        else:
            return f"Error: '{name}' sheet contains records with empty material"
