from .ReadExcelFile import ReadExcelFile
from metadata_validation_conversion.celery import app
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@app.task
def read_excel_file(conversion_type, file):
    """
    This task will convert excel file to proper json format
    :param conversion_type: could be 'samples' or 'experiments'
    :param file: file to read
    :return: converted data
    """
    channel_layer = get_channel_layer()
    if conversion_type == 'samples':

        async_to_sync(channel_layer.group_send)("submission_test_task", {
            "type": "submission_message", "status": "Waiting"})

        read_excel_file_object = ReadExcelFile(file)
        results = read_excel_file_object.start_conversion()
        async_to_sync(channel_layer.group_send)("submission_test_task", {
            "type": "submission_message", "status": "Success"})
        return results
    else:
        return 'Error: only samples are accepted now!'
