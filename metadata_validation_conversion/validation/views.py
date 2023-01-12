from django.http import HttpResponse
from celery import chord
import json
from .tasks import validate_against_schema, collect_warnings_and_additional_checks, join_validation_results, \
    collect_relationships_issues, verify_sample_ids
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message


def validate(request, action, data_type, task_id, room_id):
    send_message(room_id=room_id, validation_status="Waiting")
    conversion_result = app.AsyncResult(task_id)
    json_to_test, structure = conversion_result.get()
    # sample name should be a valid BioSampleId
    if data_type == 'samples' and action == 'update':
        reg_valid_sample_ids, erroneous_sample_ids = verify_sample_ids.apply_async((json_to_test, room_id),
                                                                                   queue='update').get()
        if erroneous_sample_ids:
            send_message(room_id=room_id,
                         validation_status=f"Erroneous BioSample IDs provided. Please check the following ids:"
                                           f"{erroneous_sample_ids}")
            return HttpResponse("Erroneous BioSample IDs provided")

    if data_type == 'samples' or data_type == 'experiments':
        # Create three tasks that should be run in parallel and assign callback
        validate_against_schema_task = validate_against_schema.s(json_to_test,
                                                                 data_type,
                                                                 structure,
                                                                 room_id=room_id).set(queue='validation')

        collect_warnings_and_additional_checks_task = collect_warnings_and_additional_checks.s(json_to_test,
                                                                                               data_type,
                                                                                               structure,
                                                                                               room_id=room_id).set(queue='validation')

        collect_relationships_issues_task = collect_relationships_issues.s(json_to_test,
                                                                           data_type,
                                                                           structure,
                                                                           action,
                                                                           room_id=room_id).set(queue='validation')

        # This will be callback for three previous tasks (just join results)
        join_validation_results_task = join_validation_results.s(room_id=room_id).set(queue='validation')

        my_chord = chord((validate_against_schema_task,
                          collect_warnings_and_additional_checks_task,
                          collect_relationships_issues_task),
                         join_validation_results_task)
    else:
        validate_against_schema_task = validate_against_schema.s(json_to_test,
                                                                 data_type,
                                                                 structure,
                                                                 room_id=room_id).set(queue='validation')

        collect_warnings_and_additional_checks_task = collect_warnings_and_additional_checks.s(json_to_test,
                                                                                               data_type,
                                                                                               structure,
                                                                                               room_id=room_id).set(queue='validation')

        join_validation_results_task = join_validation_results.s(room_id=room_id).set(
            queue='validation')
        my_chord = chord((validate_against_schema_task,
                          collect_warnings_and_additional_checks_task),
                         join_validation_results_task)
    res = my_chord.apply_async()
    return HttpResponse(json.dumps({"id": res.id}))
