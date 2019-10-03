from django.shortcuts import render
from celery import group
from .tasks import validate_against_schema, \
    collect_warnings_and_additional_checks
from metadata_validation_conversion.celery import app


def validate_samples(request, task_id):
    conversion_result = app.AsyncResult(task_id)
    json_to_test = conversion_result.get()
    validate_against_schema_task = validate_against_schema.s(json_to_test).set(
        queue='validation')
    collect_warnings_and_additional_checks_task = \
        collect_warnings_and_additional_checks.s(json_to_test).set(
            queue='validation')
    my_group = group(validate_against_schema_task,
                     collect_warnings_and_additional_checks_task)
    my_group.apply_async()
    return render(request, 'validation/validation.html')
