import xlsxwriter

from metadata_validation_conversion.constants import FIELD_NAMES
from .helpers import remove_underscores, convert_to_uppercase


class AnnotateTemplate:
    def __init__(self, json_to_convert, room_id, data_type):
        self.json_to_convert = json_to_convert
        self.room_id = room_id
        self.data_type = data_type

    def start_conversion(self):
        workbook = xlsxwriter.Workbook(f'/data/{self.room_id}.xlsx')
        cell_format_bold = workbook.add_format({'bold': True, 'font_size': 12})
        cell_format_warning = workbook.add_format(
            {'font_size': 12, 'bg_color': 'yellow'})
        cell_format_error = workbook.add_format(
            {'font_size': 12, 'bg_color': 'red'})
        cell_format = workbook.add_format({'font_size': 12})
        sheet_names = list(self.json_to_convert.keys())
        for sheet_name in sheet_names:
            worksheet = workbook.add_worksheet(remove_underscores(sheet_name))
            # Adding sample name as first column name
            column_names = list()
            column_names.append(
                FIELD_NAMES[self.data_type]['record_column_name'])
            # Adding core field names
            if self.data_type != 'analyses':
                column_names.extend(
                    self.parse_column_names(
                        self.json_to_convert[sheet_name][0][FIELD_NAMES[
                            self.data_type]['core_name']]))
            # Adding type field names
            column_names.extend(
                self.parse_column_names(self.json_to_convert[sheet_name][0]))
            # Adding modular field names
            if 'modular' in self.json_to_convert[sheet_name][0]:
                column_names.extend(self.parse_column_names(
                    self.json_to_convert[sheet_name][0]['modular']))
            # Adding custom field names
            column_names.extend(self.parse_column_names(
                self.json_to_convert[sheet_name][0]['custom']))
            # Write column names to file
            for index, name in enumerate(column_names):
                worksheet.write(0, index, name, cell_format_bold)

            # Writing data to file
            for row in range(len(self.json_to_convert[sheet_name])):
                table_data = list()
                table_warnings = list()
                table_errors = list()
                # Adding sample name as first value
                if self.data_type != 'analyses':
                    table_data.append(
                        self.json_to_convert[sheet_name][row]['custom'][
                            FIELD_NAMES[self.data_type]['record_name']][
                            'value'])
                else:
                    table_data.append(self.json_to_convert[sheet_name][row][
                                          FIELD_NAMES[self.data_type][
                                              'record_name']]['value'])
                table_warnings.append('valid')
                table_errors.append('valid')

                # Parsing core data
                if self.data_type != 'analyses':
                    parsed_data_core = self.parse_data(
                        self.json_to_convert[sheet_name][row][
                            FIELD_NAMES[self.data_type]['core_name']])
                    table_data.extend(parsed_data_core['data'])
                    table_warnings.extend(parsed_data_core['warnings'])
                    table_errors.extend(parsed_data_core['errors'])

                # Parsing type data
                parsed_data_type = self.parse_data(
                    self.json_to_convert[sheet_name][row])
                table_data.extend(parsed_data_type['data'])
                table_warnings.extend(parsed_data_type['warnings'])
                table_errors.extend(parsed_data_type['errors'])

                # Parsing modular data
                if 'modular' in self.json_to_convert[sheet_name][row]:
                    parsed_data_modular = self.parse_data(
                        self.json_to_convert[sheet_name][row]['modular'])
                    table_data.extend(parsed_data_modular['data'])
                    table_warnings.extend(parsed_data_modular['warnings'])
                    table_errors.extend(parsed_data_modular['errors'])

                # Parsing custom data
                parsed_data_custom = self.parse_data(
                    self.json_to_convert[sheet_name][row]['custom'])
                table_data.extend(parsed_data_custom['data'])
                table_warnings.extend(parsed_data_custom['warnings'])
                table_errors.extend(parsed_data_custom['errors'])

                for index, value in enumerate(table_data):
                    issues = list()
                    errors = False
                    if table_warnings[index] != 'valid':
                        issues.append(table_warnings[index])
                    if table_errors[index] != 'valid':
                        errors = True
                        issues.append(table_errors[index])
                    if len(issues) > 0 and errors:
                        worksheet.write(row + 1, index, value,
                                        cell_format_error)
                        worksheet.write_comment(row + 1, index,
                                                "\n".join(issues),
                                                {'x_scale': 2, 'y_scale': 2,
                                                 'font_size': 12})
                    elif len(issues) > 0 and not errors:
                        worksheet.write(row + 1, index, value,
                                        cell_format_warning)
                        worksheet.write_comment(row + 1, index,
                                                "\n".join(issues),
                                                {'x_scale': 2, 'y_scale': 2,
                                                 'font_size': 12})
                    else:
                        worksheet.write(row + 1, index, value, cell_format)
        workbook.close()

    def parse_column_names(self, data):
        """
        This function will return list of column names
        :param data: data to parse
        :return: list of column names
        """
        names_to_return = list()
        for k, v in data.items():
            if isinstance(v, list):
                for record in v:
                    names_to_return.extend(self.parse_column_names({k: record}))
            else:
                if k not in ['samples_core', 'custom', 'sample_name',
                             'experiments_core', 'sample_descriptor',
                             'modular', 'alias']:
                    names_to_return.append(convert_to_uppercase(k))
                    if 'term' in v:
                        names_to_return.append('Term Source ID')
                    if 'units' in v:
                        names_to_return.append('Unit')
        return names_to_return

    def parse_data(self, data):
        """
        This function will parse data and return values, errors and warnings
        :param data: data to parse
        :return: dict of lists of values, warnings and errors
        """
        data_to_return = list()
        warnings_to_return = list()
        errors_to_return = list()
        for k, v in data.items():
            if isinstance(v, list):
                for record in v:
                    parsed_data = self.parse_data({k: record})
                    data_to_return.extend(parsed_data['data'])
                    warnings_to_return.extend(parsed_data['warnings'])
                    errors_to_return.extend(parsed_data['errors'])
            else:
                if k not in ['samples_core', 'custom', 'sample_name',
                             'experiments_core', 'sample_descriptor',
                             'modular', 'alias']:
                    if 'text' in v:
                        data_to_return.append(v['text'])
                        warnings_to_return.append(
                            self.parse_issues(v, 'warnings'))
                        errors_to_return.append(self.parse_issues(v, 'errors'))
                    elif 'value' in v:
                        data_to_return.append(v['value'])
                        warnings_to_return.append(
                            self.parse_issues(v, 'warnings'))
                        errors_to_return.append(self.parse_issues(v, 'errors'))

                    if 'term' in v:
                        data_to_return.append(v['term'])
                        warnings_to_return.append(
                            self.parse_issues(v, 'warnings'))
                        errors_to_return.append(self.parse_issues(v, 'errors'))
                    elif 'units' in v:
                        data_to_return.append(v['units'])
                        warnings_to_return.append(
                            self.parse_issues(v, 'warnings'))
                        errors_to_return.append(self.parse_issues(v, 'errors'))
        return {
            'data': data_to_return,
            'warnings': warnings_to_return,
            'errors': errors_to_return
        }

    @staticmethod
    def parse_issues(data, issue_type):
        """
        This function will return string of errors
        :param data: data to parse
        :param issue_type: issue type to check
        :return: string of errors of valid if no errors
        """
        if issue_type in data:
            return "\n".join(data[issue_type])
        else:
            return 'valid'
