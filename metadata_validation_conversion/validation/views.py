from django.shortcuts import render
from celery import chord
from .tasks import validate_against_schema, \
    collect_warnings_and_additional_checks, join_validation_results
from metadata_validation_conversion.celery import app


def validate_samples(request, task_id):
    conversion_result = app.AsyncResult(task_id)
    json_to_test = conversion_result.get()
    validate_against_schema_task = validate_against_schema.s(json_to_test).set(
        queue='validation')
    collect_warnings_and_additional_checks_task = \
        collect_warnings_and_additional_checks.s(json_to_test).set(
            queue='validation')
    join_validation_results_task = join_validation_results.s().set(
        queue='validation')
    my_chord = chord((validate_against_schema_task,
                      collect_warnings_and_additional_checks_task),
                     join_validation_results_task)
    my_chord.apply_async()
    return render(request, 'validation/validation.html')
