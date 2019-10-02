from django.http import HttpResponse
from django.shortcuts import render
from .tasks import validate_against_schema
from metadata_validation_conversion.celery import app


def validate_samples(request, task_id):
    conversion_result = app.AsyncResult(task_id)
    validation_result = validate_against_schema.delay(conversion_result.get())
    return render(request, 'validation/validation.html', {
        'task_id': validation_result.id})
