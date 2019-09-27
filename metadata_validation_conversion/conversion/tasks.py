import xlrd
import json

from .helpers import get_field_names_and_indexes, get_organism_data, convert_to_snake_case
from metadata_validation_conversion.celery import app


@app.task
def read_excel_file():
    wb = xlrd.open_workbook('/Users/alexey/ebi_projects/dcc-validate-metadata/'
                            'metadata_validation_conversion/conversion/'
                            'organism.xlsx')
    sh = wb.sheet_by_index(0)
    data = list()
    headers = [convert_to_snake_case(item) for item in sh.row_values(0)]
    field_names_indexes = get_field_names_and_indexes(headers)
    for row_number in range(1, sh.nrows):
        # TODO should read sheet name and decide which json to use
        data.append(get_organism_data(sh.row_values(row_number),
                                      field_names_indexes))
    print(json.dumps(data))
    return 'Success!'
