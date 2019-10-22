import xlrd
import json

from .helpers import get_field_names_and_indexes, get_sample_data, \
    check_sheet_name_material_consistency
from metadata_validation_conversion.constants import ALLOWED_SHEET_NAMES
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import convert_to_snake_case


@app.task
def read_excel_file(conversion_type):
    """
    This task will convert excel file to proper json format
    :param conversion_type: could be 'samples' or 'experiments'
    :return: converted data
    """
    if conversion_type == 'samples':
        wb = xlrd.open_workbook(
            '/Users/alexey/ebi_projects/dcc-validate-metadata/'
            'metadata_validation_conversion/conversion/'
            'organism.xlsx')
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
    else:
        return 'Error: only samples are accepted now!'


@app.task
def upload_excel_file(file):
    with open("./file.xlsx", 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
