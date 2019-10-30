from .ReadExcelFile import ReadExcelFile
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message


@app.task
def read_excel_file(conversion_type, file):
    """
    This task will convert excel file to proper json format
    :param conversion_type: could be 'samples' or 'experiments'
    :param file: file to read
    :return: converted data
    """
    send_message('Waiting')
    if conversion_type == 'samples':
        read_excel_file_object = ReadExcelFile(file)
        results = read_excel_file_object.start_conversion()
        send_message('Success')
        return results
    else:
        return 'Error: only samples are accepted now!'
