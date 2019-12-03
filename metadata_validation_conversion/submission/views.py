import json
from django.http import HttpResponse
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from .tasks import prepare_samples_data


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
    response = HttpResponse(json.dumps(json_to_send),
                            content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="experiments.json"'
    return response


def analyses_submission(request, task_id):
    validation_result = app.AsyncResult(task_id)
    json_to_send = validation_result.get()
    response = HttpResponse(json.dumps(json_to_send),
                            content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="analyses.json"'
    return response


def send_data(request, task_id):
    conversion_results = app.AsyncResult(task_id)
    data_to_send = conversion_results.get()
    response = HttpResponse(json.dumps(data_to_send),
                            content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="samples.json"'
    return response
