from abc import ABC

from .ReadExcelFile import ReadExcelFile
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from metadata_validation_conversion.constants import ALLOWED_TEMPLATES
from celery import Task



class LogErrorsTask(Task, ABC):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        send_message(room_id=args[0], conversion_status='Error',
                     errors=f'There is a problem with the conversion process. Error: {exc}')


@app.task(base=LogErrorsTask)
def read_excel_file(room_id, conversion_type, file):
    """
    This task will convert excel file to proper json format
    :param room_id: room id to create ws url
    :param conversion_type: could be 'samples' or 'experiments'
    :param file: file to read
    :return: converted data
    """
    if conversion_type not in ALLOWED_TEMPLATES:
        send_message(
            room_id=room_id, conversion_status='Error',
            errors='This type is not supported')
        return 'Error', dict()

    read_excel_file_object = ReadExcelFile(
        file_path=file, json_type=conversion_type)
    results = read_excel_file_object.start_conversion()
    if 'Error' in results[0]:
        send_message(
            room_id=room_id, conversion_status='Error', errors=results[0])
    else:
        if results[2]:
            send_message(room_id=room_id, conversion_status='Success',
                         bovreg_submission=True)
        else:
            send_message(room_id=room_id, conversion_status='Success')
    return results[0], results[1]
