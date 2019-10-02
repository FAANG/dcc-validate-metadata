import xlrd
import json

from .helpers import get_field_names_and_indexes, get_sample_data, \
    convert_to_snake_case
from metadata_validation_conversion.constants import ALLOWED_SHEET_NAMES
from metadata_validation_conversion.celery import app


@app.task
def read_excel_file(conversion_type):
    if conversion_type == 'samples':
        wb = xlrd.open_workbook(
            '/Users/alexey/ebi_projects/dcc-validate-metadata/'
            'metadata_validation_conversion/conversion/'
            'organism.xlsx')
        wb_datemode = wb.datemode
        data = dict()
        for sh in wb.sheets():
            if sh.name not in ALLOWED_SHEET_NAMES:
                print(f"There are no rules for {sh.name} type!!!")
                return 'Failure!'
            else:
                tmp = list()
                headers = [convert_to_snake_case(item) for item in
                           sh.row_values(0)]
                field_names_indexes = get_field_names_and_indexes(
                    headers, ALLOWED_SHEET_NAMES[sh.name])
                for row_number in range(1, sh.nrows):
                    tmp.append(get_sample_data(sh.row_values(row_number),
                                               field_names_indexes,
                                               wb_datemode))
                data[convert_to_snake_case(sh.name)] = tmp
        return data
    else:
        return 'Failure!'
