import xlrd
import os
from metadata_validation_conversion.constants import ALLOWED_SHEET_NAMES, \
    SKIP_PROPERTIES, SPECIAL_PROPERTIES, JSON_TYPES, \
    SAMPLES_SPECIFIC_JSON_TYPES, EXPERIMENTS_SPECIFIC_JSON_TYPES, \
    CHIP_SEQ_INPUT_DNA_JSON_TYPES, CHIP_SEQ_DNA_BINDING_PROTEINS_JSON_TYPES, \
    EXPERIMENT_ALLOWED_SPECIAL_SHEET_NAMES, CHIP_SEQ_MODULE_RULES, \
    SAMPLE, EXPERIMENT, ANALYSIS, ID_COLUMNS_WITH_INDICES
from metadata_validation_conversion.helpers import convert_to_snake_case, \
    get_rules_json


class ReadExcelFile:
    def __init__(self, file_path, data_file_type):
        self.file_path = file_path
        self.data_file_type = data_file_type
        self.headers = list()
        self.array_fields = list()
        self.wb_datemode = None

    def start_conversion(self):
        """
        Main function that will convert xlsx file to proper json format
        :return: two values, first the message, second the submitted data in proper json format
        to report an error, the message must contains Error, suggested pattern Error: error_detail
        """
        # TODO introduce validation result object which contains status, details etc. instead of current string pattern
        wb = xlrd.open_workbook(self.file_path)
        self.wb_datemode = wb.datemode
        # keys are sheet names and values are lists of dicts, each element in the list is one row
        data = dict()
        # for frontend usage, the structure of the template
        structure = dict()
        data_specific_allowed_sheets = ALLOWED_SHEET_NAMES[self.data_file_type]

        sheets = wb.sheets()
        readme_sheet = sheets.pop(0)
        readme_flag, readme_check_result = self.check_readme_sheet(readme_sheet)
        if not readme_flag:
            os.remove(self.file_path)
            return f"Error: {readme_check_result}", structure

        for sh in sheets:
            if sh.name not in data_specific_allowed_sheets:
                if sh.name == 'faang_field_values':
                    # TODO: read in the limited values for columns, particularly for fields not in the ruleset
                    # TODO: the ones limited in ENA e.g. existing_study_type
                    continue
                elif self.data_file_type == EXPERIMENT and sh.name in EXPERIMENT_ALLOWED_SPECIAL_SHEET_NAMES:
                    special_sheet_data = self.get_experiments_additional_data(sh)
                    if 'Error' in special_sheet_data:
                        os.remove(self.file_path)
                        return special_sheet_data, structure
                    data[convert_to_snake_case(sh.name)] = special_sheet_data
                    continue
                else:
                    os.remove(self.file_path)
                    return f"Error: there are no rules for {sh.name} type!", \
                           structure
            else:
                # if no data in the sheet (only containing headers), skip the sheet
                if sh.nrows < 2:
                    continue

                if self.data_file_type in ID_COLUMNS_WITH_INDICES:
                    check_id_flag, check_id_detail = \
                        self.check_id_columns(sh, ID_COLUMNS_WITH_INDICES[self.data_file_type])
                if not check_id_flag:
                    os.remove(self.file_path)
                    return f"Error: {check_id_detail}", structure
                tmp = list()
                self.headers = [
                    convert_to_snake_case(item) for item in sh.row_values(0)]
                try:
                    field_names_indexes = self.get_field_names_and_indexes(self.data_file_type, sh.name)
                    structure[convert_to_snake_case(sh.name)] = \
                        field_names_indexes
                except ValueError as err:
                    os.remove(self.file_path)
                    return err.args[0], structure
                # read the values
                for row_number in range(1, sh.nrows):
                    sample_data = self.get_data_requiring_validation(
                        sh.row_values(row_number), field_names_indexes, sh.name)

                    material_consistency = \
                        self.check_sheet_name_material_consistency(sample_data,
                                                                   sh.name)
                    if material_consistency is not False:
                        os.remove(self.file_path)
                        return material_consistency, structure
                    if self.check_sample(sample_data):
                        tmp.append(sample_data)
                if len(tmp) > 0:
                    data[convert_to_snake_case(sh.name)] = tmp
        os.remove(self.file_path)
        return data, structure

    @staticmethod
    def check_id_columns(data_sheet, id_columns_info: dict):
        """
        check whether the data sheet contains the expected identification columns
        :param data_sheet: the sheet of the data
        :param id_columns_info: the expected column names with indices
        :return: flag and the error message (if flag is False)
        """
        headers = data_sheet.row_values(0)
        for id_column_name, id_column_index in id_columns_info.items():
            if id_column_index > len(headers) - 1:
                return False, f"The template seems to have been modified in sheet {data_sheet.name}: " \
                              f"id column {id_column_name} is expected to be at column {id_column_index+1}"
            actual_header_value = convert_to_snake_case(headers[id_column_index])
            if actual_header_value != id_column_name:
                return False, f"The template seems to have been modified in sheet {data_sheet.name}: " \
                              f"column {id_column_index+1} is expected to have column name {id_column_name}, " \
                              f"but the actual values is {actual_header_value}"
        return True, ""

    def check_readme_sheet(self, readme_sheet):
        if readme_sheet.name != 'readme':
            return False, "The first sheet of the template must have the name as readme. " \
                          "Please do not modify the structure of the provided template."

        attributes = dict()
        for row_number in range(1, readme_sheet.nrows):
            if len(str(readme_sheet.row_values(row_number)[1])):
                attr_name = str(readme_sheet.row_values(row_number)[0]).lower()
                attr_value = str(readme_sheet.row_values(row_number)[1]).lower()
                attributes[attr_name] = attr_value
        if attributes and 'type' in attributes:
            template_type = attributes['type']
            if template_type != self.data_file_type:
                return False, f"The selected validation type is {self.data_file_type}, " \
                              f"however the template is for {template_type} type"
        else:
            return False, "Could not find template type information in the readme sheet. " \
                          "Please do not modify the provided template."
        return True, ""

    def get_experiments_additional_data(self, sheet):
        """
        This function will parse non assay type specific sheets in the experiment template
        the returned data is a list of rows, each row is represented as a dict with filed name as key and value as value
        :param sheet: object to get data from
        :return: parsed data
        """
        sheet_name = sheet.name
        data = list()
        sheet_fields = EXPERIMENT_ALLOWED_SPECIAL_SHEET_NAMES[sheet_name]
        for row_number in range(1, sheet.nrows):
            tmp = dict()
            for index, field_name in enumerate(sheet_fields['all']):
                try:
                    tmp[field_name] = sheet.row_values(row_number)[index]
                    # Convert date data to string (as Excel stores date in float format)
                    # According to https://xlrd.readthedocs.io/en/latest/dates.html, using this package’s
                    # xldate_as_tuple() function to convert numbers from a workbook, you must use
                    # the datemode attribute of the WorkBook object
                    # has to be hard-coded as only run_date requires dateTime type, all others use date type
                    if field_name == 'run_date':
                        date_value = sheet.row_values(row_number)[index]
                        if isinstance(date_value, float):
                            # noinspection PyPep8Naming
                            y, m, d, H, M, S = xlrd.xldate_as_tuple(sheet.row_values(row_number)[index], self.wb_datemode)
                            m = self.add_leading_zero(m)
                            d = self.add_leading_zero(d)
                            # noinspection PyPep8Naming
                            H = self.add_leading_zero(H)
                            # noinspection PyPep8Naming
                            M = self.add_leading_zero(M)
                            # noinspection PyPep8Naming
                            S = self.add_leading_zero(S)
                            cell_value = f"{y}-{m}-{d}T{H}:{M}:{S}"
                            tmp[field_name] = cell_value
                        elif isinstance(date_value, str):
                            if 'T' in date_value:
                                tmp[field_name] = date_value
                            else:
                                tmp[field_name] = f"{date_value}T00:00:00"
                        else:
                            return f"Error: run_date field has unrecognized value {date_value}"

                except IndexError:
                    if field_name in sheet_fields['mandatory']:
                        return f'Error: {field_name} field is mandatory in sheet {sheet_name}'
                if field_name in sheet_fields['mandatory'] \
                        and tmp[field_name] == '':
                    return f'Error: mandatory field {field_name} in sheet {sheet_name} cannot have empty value'
            data.append(tmp)
        return data

    def get_field_names_and_indexes(self, data_file_type, sheet_name):
        # TODO: discuss with Alexey the logic of this function
        # Propose to read template to get field-index dict
        # read the ruleset to 1) check whether all mandatory fields there 2) split into 4 sections
        # current logic: read the ruleset, for every column the template needs to be read once
        """
        This function will create dict with field_names as keys and field
        sub_names
        with its indices inside template as values
        :return dict with core and type field_names and indexes
        """
        field_names = dict()
        array_fields = list()
        field_names_and_indexes = dict()
        # get the sheet sheet_name specific ruleset url
        url = ALLOWED_SHEET_NAMES[data_file_type][sheet_name]
        # TODO: check whether sheet is empty or not before loading ruleset. If empty, no need to load
        # Check for chip-seq module rules
        if sheet_name in CHIP_SEQ_MODULE_RULES:
            type_section_json, core_section_json, module_section_json = get_rules_json(
                url, self.data_file_type, CHIP_SEQ_MODULE_RULES[sheet_name])
            field_names['module'], tmp = self.parse_json(module_section_json)
            array_fields.extend(tmp)
            field_names['core'], tmp = self.parse_json(core_section_json)
            array_fields.extend(tmp)
        elif data_file_type == ANALYSIS:  # analysis type only have one rule set (type)
            type_section_json = get_rules_json(url, self.data_file_type)
        else:
            type_section_json, core_section_json = get_rules_json(url, self.data_file_type)
            field_names['core'], tmp = self.parse_json(core_section_json)
            array_fields.extend(tmp)

        field_names['type'], tmp = self.parse_json(type_section_json)
        array_fields.extend(tmp)
        field_names['custom'], tmp = self.get_custom_data_fields(field_names,
                                                                 sheet_name)
        array_fields.extend(tmp)

        # Add column index based on the field sheet_name
        # {'core': {'assay_type': ['value'], 'sample_storage': ['value'],..},...}
        # convert to {'core': {'assay_type': {'value': 1}, 'sample_storage': {'value': 2},...},...}
        for ruleset_section, section_details in field_names.items():
            subtype_name_and_indexes = dict()
            for field_name, field_types in section_details.items():
                subtype_name_and_indexes[field_name] = self.get_indices(
                    field_name, field_types, array_fields)
            field_names_and_indexes[ruleset_section] = subtype_name_and_indexes
        return field_names_and_indexes

    @staticmethod
    def parse_json(json_to_parse):
        """
        This function will parse ruleset in json
        :param json_to_parse: json file (not link) that should be parsed
        :return: dict with field_names as keys and expected sub field list as values
                e.g. {'organism': ['text', 'term'], 'birth_date': ['value', 'units'], 'health_status': ['text', 'term']}
                 and fields which allow multiple values, e.g. ['health_status', 'child_of']
        """
        # example json: https://raw.githubusercontent.com/FAANG/dcc-metadata/switch_to_json-schema/json_schema
        # /type/samples/faang_samples_organism.metadata_rules.json
        # which has both array and object types
        required_fields = dict()
        allow_multiple_fields = list()
        for field_name, field_details in json_to_parse['properties'].items():
            if field_name not in SKIP_PROPERTIES:
                # currently the ruleset only has two types: object or array,
                # array is for fields which allows multiple values
                # single value uses object type, even actually it is a string type, e.g. project = FAANG
                required_fields.setdefault(field_name, [])
                if field_details['type'] == 'object':
                    for sc_property in field_details['required']:
                        required_fields[field_name].append(sc_property)
                elif field_details['type'] == 'array':
                    allow_multiple_fields.append(field_name)
                    for sc_property in field_details['items']['required']:
                        required_fields[field_name].append(sc_property)
        return required_fields, allow_multiple_fields

    def get_custom_data_fields(self, field_names, sheet_name):
        """
        This function will go through headers and find all remaining names that
        are not in FAANG ruleset
        :param field_names: names from json-schema
        :param sheet_name: name of the template sheet
        :return: rules for custom fields in dict and all array fields
        """
        custom_data_fields_indexes = dict()
        allow_multiple_fields = list()
        # headers_to_check contains all field names corresponding to the current sheet sheet_name
        # example for ataq-seq sheet in experiment
        #      core ruleset part                                       type ruleset part
        # {'assay_type': ['value'], 'sample_storage': ['value'], ..., transposase_protocol': ['value']}
        # TODO: add test case: template having both BS-seq and Hi-C as both of them have the same restriction enzyme
        if sheet_name in CHIP_SEQ_MODULE_RULES:
            headers_to_check = {**field_names['core'], **field_names['type'],
                                **field_names['module']}
        elif self.data_file_type == ANALYSIS:
            headers_to_check = {**field_names['type']}
        else:
            headers_to_check = {**field_names['core'], **field_names['type']}
        # self.headers is assigned when the sheet is being read, in snake case
        # NOTE: current implementation all fields including core ruleset fields are present in a single sheet,
        # not like old template which is split into experiment ena, experiment faang, assay-type specific
        id_columns = list()
        if self.data_file_type in ID_COLUMNS_WITH_INDICES:
            id_columns = ID_COLUMNS_WITH_INDICES[self.data_file_type]
        for header in self.headers:
            # SPECIAL_PROPERTIES: special conserved headers, e.g. unit
            # TODO: add test case in the same sheet duplicate columns should same layout
            #  (sheet_name | sheet_name+unit| sheet_name+ontolgoy id), if mixed, needs to be reported as error
            if header not in headers_to_check and header not in \
                    SPECIAL_PROPERTIES and header not in id_columns:
                indexes = self.return_all_indexes(header)
                # multiple values are expected to be presented as duplicated columns in the template
                if len(indexes) > 1:
                    allow_multiple_fields.append(header)
                # check
                if len(self.headers)-1 > (indexes[0] + 1) and \
                        self.headers[indexes[0] + 1] == 'unit':
                    custom_data_fields_indexes[header] = ['value', 'units']
                elif len(self.headers)-1 > (indexes[0] + 1) and \
                        self.headers[indexes[0] + 1] == 'term_source_id':
                    custom_data_fields_indexes[header] = ['text', 'term']
                else:
                    custom_data_fields_indexes[header] = ['value']
        return custom_data_fields_indexes, allow_multiple_fields

    def return_all_indexes(self, item_to_check):
        """
        This function will return array of all indexes of item in array
        :param item_to_check: item to search
        :return:
        """
        return [index for index, value in enumerate(self.headers) if value ==
                item_to_check]

    def get_indices(self, field_name, field_types, array_fields):
        """
        This function will return position of fields in template
        :param field_name: name of the field in the template
        :param field_types: types that this field has
        :param array_fields: the list of fields which allow multiple values
        :return: dict with positions of types of field
        """
        if field_name not in self.headers:
            raise ValueError(
                f"Error: can't find this property '{field_name}' in "
                f"headers")
        # in the current design, when only one column expected for one field, that column must be 'value'
        if len(field_types) == 1:
            indices = self.return_all_indexes(field_name)
            if len(indices) == 1 and field_name not in array_fields:
                return {'value': indices[0]}
            elif field_name in array_fields:
                indices_list = list()
                for index in indices:
                    indices_list.append({'value': index})
                return indices_list
            else:
                raise ValueError(f"Error: multiple entries for attribute "
                                 f"'{field_name}' present")
        else:
            if field_types == ['value', 'units'] or field_types == ['text', 'term']:
                value_indices = self.return_all_indexes(field_name)
                if len(value_indices) == 1 and field_name not in array_fields:
                    return self.check_field_existence(value_indices[0],
                                                      field_name, field_types[0], field_types[1])
                elif field_name in array_fields:
                    indices_list = list()
                    for index in value_indices:
                        indices_list.append(
                            self.check_field_existence(index, field_name, field_types[0], field_types[1]))
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
        This function will check whether table has all required subfields,
        for example, ontology id expect to have text and term two subfields
        :param index: index to check in table
        :param field: field name
        :param first_subfield: first subfield name
        :param second_subfield: second subfield name
        :return: dict with subfield indexes
        """
        # subfield_to_check is the snake cased column header used in the template
        if second_subfield == 'units':
            subfield_to_check = 'unit'
        elif second_subfield == 'term':
            subfield_to_check = 'term_source_id'

        if self.headers[index + 1] != subfield_to_check:
            raise ValueError(
                f"Error: this property {field} doesn't have {subfield_to_check} "
                f"provided in template!")
        return {first_subfield: index, second_subfield: index + 1}

    def get_data_requiring_validation(self, row_data, field_names_indexes, sheet_name):
        """
        This function will fetch information about organism
        :param row_data: row from template to fetch information from
        :param field_names_indexes: dict with field names and indexes from json
        :param sheet_name: name of the sheet
        :return: dict with required information
        """
        data_to_validate = dict()
        # ruleset_section_types indicates which ruleset will be applied to the current sheet
        # e.g. {'core': 'experiments_core', 'type': None, 'custom': 'custom'}
        if sheet_name == 'chip-seq input dna':
            ruleset_section_types = {**EXPERIMENTS_SPECIFIC_JSON_TYPES, **JSON_TYPES,
                          **CHIP_SEQ_INPUT_DNA_JSON_TYPES}
        elif sheet_name == 'chip-seq dna-binding proteins':
            ruleset_section_types = {**EXPERIMENTS_SPECIFIC_JSON_TYPES, **JSON_TYPES,
                          **CHIP_SEQ_DNA_BINDING_PROTEINS_JSON_TYPES}
        else:
            if self.data_file_type == SAMPLE:
                ruleset_section_types = {**SAMPLES_SPECIFIC_JSON_TYPES, **JSON_TYPES}
            elif self.data_file_type == ANALYSIS:
                ruleset_section_types = {**JSON_TYPES}
            else:
                ruleset_section_types = {**EXPERIMENTS_SPECIFIC_JSON_TYPES, **JSON_TYPES}

        for section_type, section_pointer in ruleset_section_types.items():
            if section_pointer is not None:
                data_to_validate.setdefault(section_pointer, dict())
                for field_name, indexes in field_names_indexes[section_type].items():
                    date_field_flag = self.check_cell_is_date(field_name)
                    self.add_row(field_name, indexes, data_to_validate[section_pointer],
                                 row_data, date_field_flag)
            else:
                for field_name, indexes in field_names_indexes[section_type].items():
                    date_field_flag = self.check_cell_is_date(field_name)
                    self.add_row(field_name, indexes, data_to_validate,
                                 row_data, date_field_flag)
        return data_to_validate

    @staticmethod
    def check_cell_is_date(field_name):
        """
        This function will check that current column is date field
        :param field_name: header of the column
        :return: True if column header contains 'date' and False otherwise
        """
        if 'date' in field_name:
            return True
        else:
            return False

    def add_row(self, field_name, indexes, organism_to_validate, input_data,
                date_field):
        """
        High-level function to get data from table
        :param field_name: sheet_name of the field to add
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
        :param fields: dict with field sheet_name as key and field index as value
        :return: dict with required information
        """
        data_to_return = dict()
        for field_name, field_index in fields.items():
            cell_value = input_data[field_index]
            if cell_value != '':
                # Convert all "_" in term ids to ":" as required by validator
                if field_name == 'term' and "_" in cell_value:
                    cell_value = cell_value.replace("_", ":")
                # Convert date data to string (as Excel stores date in float format)
                # According to https://xlrd.readthedocs.io/en/latest/dates.html, using this package’s xldate_as_tuple()
                # function to convert numbers from a workbook, you must use the datemode attribute of the Book object
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
        :param field_name: sheet_name of field
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

    def check_sheet_name_material_consistency(self, sample_data, sheet_name):
        """
        This function checks that sheet has consistent material
        :param sample_data: data to check
        :param sheet_name: name of sheet
        :return: False or error message
        """
        if self.data_file_type != SAMPLE:
            return False
        if 'samples_core' in sample_data and 'material' in \
                sample_data['samples_core'] and 'text' in \
                sample_data['samples_core']['material']:
            material = sample_data['samples_core']['material']['text']
            if material != sheet_name:
                return f"Error: '{sheet_name}' sheet contains record with " \
                       f"inconsistent material '{material}'"
            else:
                return False
        else:
            return f"Error: '{sheet_name}' sheet contains records with empty material"

    @staticmethod
    def check_sample(sample):
        """
        This function will check that sample is not empty
        :param sample: sample to check
        :return: True if sample should be added to data and False otherwise
        """
        if 'experiments_core' in sample and len(sample) <= 3:
            if 'input_dna' in sample:
                if len(sample['input_dna']) > 0:
                    return True
                return False
            elif 'binding_proteins' in sample:
                if len(sample['binding_proteins']) > 0:
                    return True
                return False
            else:
                return False
        return True
