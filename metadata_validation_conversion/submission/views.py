import json
from django.http import HttpResponse
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from .tasks import prepare_samples_data, prepare_analyses_data, \
    prepare_experiments_data
from .helpers import zip_files


def samples_submission(request, task_id):
    send_message(submission_status='Preparing data')
    validation_result = app.AsyncResult(task_id)
    json_to_send = validation_result.get()
    prepare_samples_data_task = prepare_samples_data.s(json_to_send).set(
        queue='submission')
    res = prepare_samples_data_task.apply_async()
    return HttpResponse(json.dumps({"id": res.id}))


def experiments_submission(request, task_id):
    validation_result = app.AsyncResult(task_id)
    json_to_send = validation_result.get()
    prepare_experiments_data_task = prepare_experiments_data.s(
        json_to_send).set(queue='submission')
    res = prepare_experiments_data_task.apply_async()
    return HttpResponse(json.dumps({"id": res.id}))


def analyses_submission(request, task_id):
    validation_result = app.AsyncResult(task_id)
    json_to_send = validation_result.get()
    prepare_analyses_data_task = prepare_analyses_data.s(json_to_send).set(
        queue='submission')
    res = prepare_analyses_data_task.apply_async()
    return HttpResponse(json.dumps({"id": res.id}))


def send_data(request, task_id):
    conversion_results = app.AsyncResult(task_id)
    data_to_send = conversion_results.get()
    if isinstance(data_to_send, list):
        if data_to_send[0] == 'analysis':
            filename = 'analyses.zip'
        else:
            filename = 'experiments.zip'
        zipped_file = zip_files(data_to_send[1:], data_to_send[0])
        response = HttpResponse(zipped_file,
                                content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    else:
        response = HttpResponse(json.dumps(data_to_send),
                                content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="samples.json"'
    return response
