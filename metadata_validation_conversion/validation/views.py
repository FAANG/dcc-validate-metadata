from django.http import HttpResponse
from .tasks import validate_against_schema
from metadata_validation_conversion.celery import app


def validate_samples(request, task_id):
    result = app.AsyncResult(task_id)
    validate_against_schema.delay(result.get())
    return HttpResponse("Started validation!")
