import json
from django.http import HttpResponse
from metadata_validation_conversion.celery import app


def samples_submission(request, task_id):
    validation_result = app.AsyncResult(task_id)
    json_to_send = validation_result.get()
    response = HttpResponse(json.dumps(json_to_send),
                            content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="samples.json"'
    return response


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
