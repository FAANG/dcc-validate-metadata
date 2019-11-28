from django.http import HttpResponse
from celery import chord
from .tasks import validate_against_schema, \
    collect_warnings_and_additional_checks, join_validation_results, \
    collect_relationships_issues
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message


def validate_samples(request, task_id):
    send_message(validation_status="Waiting")
    conversion_result = app.AsyncResult(task_id)
    json_to_test = conversion_result.get()
    # Create three tasks that should be run in parallel and assign callback
    validate_against_schema_task = validate_against_schema.s(json_to_test,
                                                             'samples').set(
        queue='validation')
    collect_warnings_and_additional_checks_task = \
        collect_warnings_and_additional_checks.s(json_to_test, 'samples').set(
            queue='validation')
    collect_relationships_issues_task = collect_relationships_issues.s(
        json_to_test).set(queue='validation')
    # This will be callback for three previous tasks (just join results)
    join_validation_results_task = join_validation_results.s().set(
        queue='validation')
    my_chord = chord((validate_against_schema_task,
                      collect_warnings_and_additional_checks_task,
                      collect_relationships_issues_task),
                     join_validation_results_task)
    my_chord.apply_async()
    return HttpResponse(my_chord.id)


def validate_experiments(request, task_id):
    send_message(validation_status="Waiting")
    conversion_result = app.AsyncResult(task_id)
    json_to_test = conversion_result.get()
    validate_against_schema_task = validate_against_schema.s(json_to_test,
                                                             'experiments').set(
        queue='validation')
    collect_warnings_and_additional_checks_task = \
        collect_warnings_and_additional_checks.s(
            json_to_test, 'experiments').set(queue='validation')
    join_validation_results_task = join_validation_results.s().set(
        queue='validation')
    my_chord = chord((validate_against_schema_task,
                      collect_warnings_and_additional_checks_task),
                     join_validation_results_task)
    my_chord.apply_async()
    return HttpResponse("Starting validation")
