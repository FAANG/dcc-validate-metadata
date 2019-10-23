import json
from .ReadExcelFile import ReadExcelFile
from metadata_validation_conversion.celery import app


@app.task
def read_excel_file(conversion_type, file):
    """
    This task will convert excel file to proper json format
    :param conversion_type: could be 'samples' or 'experiments'
    :param file: file to read
    :return: converted data
    """
    if conversion_type == 'samples':
        read_excel_file_object = ReadExcelFile(file)
        results = read_excel_file_object.start_conversion()
        # print(json.dumps(results))
        return results
    else:
        return 'Error: only samples are accepted now!'
