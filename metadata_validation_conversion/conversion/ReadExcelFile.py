import xlrd

from metadata_validation_conversion.constants import ALLOWED_SHEET_NAMES
from .helpers import get_field_names_and_indexes, get_sample_data, \
    check_sheet_name_material_consistency
from metadata_validation_conversion.helpers import convert_to_snake_case


class ReadExcelFile:
    def __init__(self, file_path):
        self.file_path = file_path

    def start_conversion(self):
        wb = xlrd.open_workbook(self.file_path)
        wb_datemode = wb.datemode
        data = dict()
        for sh in wb.sheets():
            if sh.name not in ALLOWED_SHEET_NAMES:
                return f"Error: there are no rules for {sh.name} type!"
            else:
                tmp = list()
                headers = [convert_to_snake_case(item) for item in
                           sh.row_values(0)]
                try:
                    field_names_indexes = \
                        get_field_names_and_indexes(headers,
                                                    ALLOWED_SHEET_NAMES[
                                                        sh.name])
                except ValueError as err:
                    return err.args[0]
                for row_number in range(1, sh.nrows):
                    sample_data = get_sample_data(sh.row_values(row_number),
                                                  field_names_indexes,
                                                  wb_datemode)
                    material_consistency = \
                        check_sheet_name_material_consistency(
                            sample_data, sh.name)
                    if material_consistency is not False:
                        return material_consistency
                    tmp.append(sample_data)
                data[convert_to_snake_case(sh.name)] = tmp
        return data
