"""
The main script which reads in the Excel file and the corresponding rulesets
Steps
1. Initialize with the Excel file path
2. Preliminary check: contains readme sheet? the right template used?
3. Read in the core ruleset which applies to all data in the template (except the special sheets in Experiment template)
4. Iterate all sheets in the template file
    a. special sheets: e.g. allowed value sheet, related to submission sheets including runs, studies etc
    b. Normal sheet
    c. Unexpected sheet: report error
5. For each normal sheet
    a. if empty, skip
    b. check whether all expected id columns exist (id columns are do expected in the ruleset)
        i. if yes, continue
        ii. if no, report the error to the user
    c. load the corresponding type/module ruleset and work out which columns are mandatory
    d. check the template against the ruleset for three things
        i.  all fields with multiple values are allowed to have multiple values in the ruleset
        ii. if any mandatory field missing, report to the user for correction
        iii. any unaccounted for fields will be classified as custom fields
    e. read each line
        i. check whether each row has values for id columns (mutliple id columns allowed which means that
            the key for the record is the combination of all id columns)
        ii. check all mandatory fields contain value (the validity of the value will be checked later)
"""
import xlrd
import os
from metadata_validation_conversion.constants import ALLOWED_SHEET_NAMES, \
    SKIP_PROPERTIES, SPECIAL_PROPERTIES, JSON_TYPES, \
    SAMPLES_SPECIFIC_JSON_TYPES, EXPERIMENTS_SPECIFIC_JSON_TYPES, \
    CHIP_SEQ_INPUT_DNA_JSON_TYPES, CHIP_SEQ_DNA_BINDING_PROTEINS_JSON_TYPES, SPECIAL_SHEETS, \
    SAMPLE, EXPERIMENT, ANALYSIS, ID_COLUMNS_WITH_INDICES, MINIMUM_TEMPLATE_VERSION_REQUIREMENT
from metadata_validation_conversion.helpers import convert_to_snake_case, \
    get_core_ruleset_json, get_type_ruleset_json, get_module_ruleset_json


class ReadExcelFile:
    def __init__(self, file_path, data_file_type):
        self.file_path = file_path
        self.data_file_type = data_file_type
        self.headers = list()
        self.array_fields = list()
        self.wb_datemode = None
        self.rulesets = dict()

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
        # Step 2: Preliminary check: contains readme sheet? the right template used?
        sheets = wb.sheets()
        # readme sheet is expected to always be the first sheet
        readme_sheet = sheets.pop(0)
        readme_flag, readme_check_result = self.check_readme_sheet(readme_sheet)
        if not readme_flag:
            os.remove(self.file_path)
            return f"Error: {readme_check_result}", structure
        # Step 3: Read in the core ruleset
        self.rulesets['core'] = get_core_ruleset_json(self.data_file_type)

        # Step 4: Iterate all sheets
        # the expected sheets according to data type
        data_specific_allowed_sheets = ALLOWED_SHEET_NAMES[self.data_file_type]
        for sh in sheets:
            sheet_name = convert_to_snake_case(sh.name)
            if sheet_name not in data_specific_allowed_sheets:
                if sheet_name == 'faang_field_values':
                    # TODO: read in the limited values for columns, particularly for fields not in the ruleset
                    # TODO: the ones limited in ENA e.g. existing_study_type
                    continue
                elif self.data_file_type in SPECIAL_SHEETS:
                    special_sheet_list = SPECIAL_SHEETS[self.data_file_type]
                    if sheet_name in special_sheet_list:
                        expected_special_fields = special_sheet_list[sheet_name]
                        special_sheet_data = self.get_special_sheet_data(sh, expected_special_fields)
                        if 'Error' in special_sheet_data:
                            os.remove(self.file_path)
                            return special_sheet_data, structure
                        data[sheet_name] = special_sheet_data
                        continue
                    else:
                        os.remove(self.file_path)
                        return f"Error: there are no rules for {sh.name} type!", \
                               structure
                else:
                    os.remove(self.file_path)
                    return f"Error: there are no rules for {sh.name} type!", \
                           structure
            # Step 5: Normal sheet
            else:
                print(sh.name)
                # Step 5a: if no data in the sheet (only containing headers), skip the sheet
                if sh.nrows < 2:
                    continue
                # Step 5b: check id columns
                id_columns = list()
                if self.data_file_type in ID_COLUMNS_WITH_INDICES:
                    id_columns = ID_COLUMNS_WITH_INDICES[self.data_file_type]
                    check_id_flag, check_id_detail = self.check_id_columns(sh, id_columns)
                if not check_id_flag:
                    os.remove(self.file_path)
                    return f"Error: {check_id_detail}", structure

                # Step 5c: Load type and module ruleset
                # read the json files of the rulesets from dcc-metadata repository
                snaked_sheet_name = convert_to_snake_case(sh.name)
                self.rulesets['type'] = get_type_ruleset_json(self.data_file_type, snaked_sheet_name)
                self.rulesets['module'] = get_module_ruleset_json(self.data_file_type, snaked_sheet_name)
                # convert the json-schema ruleset into field names
                field_names = dict()
                multiple_values_field_list = list()
                mandatory_field_list = list()
                for ruleset_type, section_detail in self.rulesets.items():
                    if section_detail is not None:
                        field_names[ruleset_type], tmp_multiple, tmp_mandatory = \
                            self.parse_ruleset_json(section_detail)
                        multiple_values_field_list.extend(tmp_multiple)
                        mandatory_field_list.extend(tmp_mandatory)
                # get all field names which will be used to
                # determine and process custom fields (fields not in the ruleset)
                all_field_names_in_ruleset = set()
                for section_detail in field_names.values():
                    if section_detail is not None:
                        for field_name in section_detail:
                            all_field_names_in_ruleset.add(field_name)

                # Step 5d: check the template against the ruleset
                # read in the headers in the current sheet and process
                headers_in_template = dict()
                # for display purpose to keep the original header, the keys in headers_in_template are snake cased
                multiple_header_field_dict = dict()
                for location, header in enumerate(sh.row_values(0)):
                    header = convert_to_snake_case(header)
                    # header as unit and term source id should have already been dealt with
                    if header in SPECIAL_PROPERTIES:
                        continue
                    main, additional = self.determine_subfields(sh.row_values(0), location)
                    if header in headers_in_template:  # has been dealt with already, i.e. multiple
                        if main != headers_in_template[header]['main'] or \
                                additional != headers_in_template[header]['additional']:
                            return f"Error: In the sheet {sh.name}, column {sh.row_values(0)[location]} " \
                                   f"has multiple appearances but different structure", structure
                        multiple_header_field_dict[header] = sh.row_values(0)[location]
                        headers_in_template[header]['location'].append(location)
                    else:
                        headers_in_template.setdefault(header, dict())
                        headers_in_template[header].setdefault('location', list())
                        headers_in_template[header]['location'].append(location)
                        headers_in_template[header]['main'] = main
                        headers_in_template[header]['additional'] = additional

                # 5di: check whether multiple values allowed
                for tmp in multiple_header_field_dict:
                    # only check fields in the ruleset
                    if tmp in all_field_names_in_ruleset and tmp not in multiple_values_field_list:
                        return f"Error: In the sheet {sh.name}, column {multiple_header_field_dict[tmp]} " \
                               f"has multiple values which is not allowed in the ruleset", structure
                # 5d ii: check all mandatory fields exist in the template
                for tmp in mandatory_field_list:
                    if tmp not in headers_in_template:
                        return f"Error: the mandatory field {tmp.replace('_',' ')} could not be found " \
                               f"in the {sh.name} sheet", structure
                # 5d iii: map template to the ruleset (field_names) to add locations into it (field_names_with_indices)
                # meanwhile work out the fields in the template are not in the ruleset
                # those fields will be listed as custom fields

                not_found = headers_in_template
                field_names_with_indices = dict()
                for ruleset_type, section_ruleset_detail in field_names.items():
                    section_with_indices = dict()
                    for field_name, field_subfields_in_ruleset in section_ruleset_detail.items():
                        field_in_template = headers_in_template[field_name]
                        field_mapped = self.map_field_for_locations(field_name, field_in_template,
                                                                    field_subfields_in_ruleset)
                        # only return string (error message) when there is an error
                        if type(field_mapped) is str:
                            return field_mapped, structure
                        section_with_indices[field_name] = field_mapped
                        not_found.pop(field_name)
                    field_names_with_indices[ruleset_type] = section_with_indices
                # work out custom fields
                field_names_with_indices['custom'] = self.extract_custom_fields(not_found)

                # self.headers = [
                #     convert_to_snake_case(item) for item in sh.row_values(0)]
                tmp = list()
                for row_number in range(1, sh.nrows):
                    row_data = self.get_data_requiring_validation(
                        sh.row_values(row_number), field_names_with_indices, sh.name)
                    material_consistency = \
                        self.check_sheet_name_material_consistency(row_data,
                                                                   sh.name)
                    # if sh.name == 'cage-seq':
                    #     import json
                    #     print(json.dumps(row_data))
                    #     print(material_consistency)
                    #     print(self.check_record(row_data))
                    if material_consistency is not False:
                        os.remove(self.file_path)
                        return material_consistency, structure
                    if self.check_record(row_data):
                        tmp.append(row_data)
                if len(tmp) > 0:
                    data[convert_to_snake_case(sh.name)] = tmp
        os.remove(self.file_path)
        return data, structure

    @staticmethod
    def determine_subfields(headers, location):
        """
        determine the data type of the particular header according to the location
        :param headers: the header row in the template
        :param location: the location
        :return: the list of expected sub-fields
        """
        if location >= len(headers) - 1:
            return 'value', None
        next_header = headers[location+1]
        next_header = convert_to_snake_case(next_header)
        if next_header == 'unit':
            return 'value', 'units'
        elif next_header == 'term_source_id':
            return 'text', 'term'
        else:
            return 'value', None

    @staticmethod
    def map_field_for_locations(field_name, field_in_template, field_subfields_in_ruleset):
        """
        map one field from ruleset to template to get column location information
        :param field_name: the name of the field
        :param field_in_template: the map of column(s) with the field name in the given template
        e.g.
        :param field_subfields_in_ruleset: the list of the expected subfields in the ruleset,
        e.g. ['value'], or ['text','term']
        :return: the location-mapped result (list for multiple or dict for single value) or the error message
        """
        if len(field_subfields_in_ruleset) == 1:  # just 'value' for the field
            if field_in_template['additional'] is not None:
                return f"Error: Field {field_name} only expects a value, please check the provided template"
            if len(field_in_template['location']) == 1:  # single value
                result = dict()
                result[field_in_template['main']] = field_in_template['location'][0]
            else:  # multiple values for the field
                result = list()
                for loc in field_in_template['location']:
                    result.append({field_in_template['main']: loc})
        else:  # either ['value', 'units'] or ['text', 'term']
            if field_in_template['main'] != field_subfields_in_ruleset[0] or \
                    field_in_template['additional'] != field_subfields_in_ruleset[1]:
                return f"Error: the field {field_name} does not match the corresponding ruleset"
            if len(field_in_template['location']) == 1:  # single value
                result = dict()
                result[field_subfields_in_ruleset[0]] = field_in_template['location'][0]
                result[field_subfields_in_ruleset[1]] = field_in_template['location'][0] + 1
            else:
                result = list()
                for loc in field_in_template['location']:
                    tmp = dict()
                    tmp[field_subfields_in_ruleset[0]] = loc
                    tmp[field_subfields_in_ruleset[1]] = loc + 1
                    result.append(tmp)
        return result

    def extract_custom_fields(self, not_found):
        """
        extract custom fields from the fields not mapped in the template
        :param not_found: the dict of fields present in the template but not mapped to rulesets
        :return: custom fields
        """
        # custom fields are the fields not in the ruleset, apart from this,
        # the returned structure should be exactly the same as the structure returned from fields having rulesets
        # hence logical to re-use the method (map_field_for_locations) which generates the structure for ruleset fields
        # the only thing needs to do is to create the artificial field_subfields_in_ruleset
        result = dict()
        print(not_found)
        for field_name, field_in_template in not_found.items():
            # create the artificial variable
            if field_in_template['additional'] is None:
                artificial_subfields = [field_in_template['main']]
            else:
                artificial_subfields = [field_in_template['main'], field_in_template['additional']]
            result[field_name] = self.map_field_for_locations(field_name, field_in_template, artificial_subfields)
        return result


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
        """
        Check the content of the readme sheet, currently check two things: version and type of the template
        :param readme_sheet: the readme sheet in the template
        :return: check result (True or False) and details
        """
        if readme_sheet.name != 'readme':
            return False, "The first sheet of the template must have the name as readme. " \
                          "Please do not modify the structure of the provided template."

        attributes = dict()
        for row_number in range(1, readme_sheet.nrows):
            # check 2nd cell of each row, if not empty, assume to be the attribute value
            # if empty, then it is the description of the template, ignored
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

        template_version = 0
        if attributes and 'template version' in attributes:
            try:
                template_version = float(attributes['template version'])
            except ValueError:
                return False, f"The value provided for template version" \
                              f" ({attributes['template version']}) is not a valid number"
        if template_version < MINIMUM_TEMPLATE_VERSION_REQUIREMENT:
            if template_version == 0:
                return False, f"Missing template version information in the readme sheet"
            else:
                return False, f"Please re-download the template from data.faang.org as the template you are using " \
                              f"(version {template_version}) is out of date and no longer supported."
        return True, ""

    def get_special_sheet_data(self, sheet, sheet_fields):
        """
        This function will parse non assay type specific sheets
        in the template (currently only existing in experiment template)
        the returned data is a list of rows, each row is represented as a dict with filed name as key and value as value
        :param sheet: object to get data from
        :param sheet_fields: the expected fields for the special sheet defined in the constants.py
        :return: parsed data
        """
        sheet_name = sheet.name
        data = list()
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

    @staticmethod
    def parse_ruleset_json(json_to_parse):
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
        mandatory_fields = list()
        for field_name, field_details in json_to_parse['properties'].items():
            if field_name not in SKIP_PROPERTIES:
                # currently the ruleset only has two types: object or array,
                # array is for fields which allows multiple values, e.g. health status in sample
                # single value uses object type, even actually it is a string type, e.g. project = FAANG
                required_fields.setdefault(field_name, [])
                # for the array type, the details is a level deeper
                if field_details['type'] == 'array':
                    allow_multiple_fields.append(field_name)
                    field_details = field_details['items']
                for sc_property in field_details['required']:
                    required_fields[field_name].append(sc_property)
                if field_details['properties']['mandatory']['const'] == 'mandatory':
                    mandatory_fields.append(field_name)
        return required_fields, allow_multiple_fields, mandatory_fields

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
    def check_record(record):
        """
        This function will check that record is not empty
        :param record: record to check
        :return: True if record should be added to data and False otherwise
        """
        if 'experiments_core' in record and len(record) <= 3:
            if 'input_dna' in record:
                if len(record['input_dna']) > 0:
                    return True
                return False
            elif 'binding_proteins' in record:
                if len(record['binding_proteins']) > 0:
                    return True
                return False
            else:
                return False
        return True
