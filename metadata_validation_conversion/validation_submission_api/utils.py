from metadata_validation_conversion.constants import ALLOWED_TEMPLATES
from conversion.ReadExcelFile import ReadExcelFile
from validation.tasks import validate_against_schema, \
    collect_warnings_and_additional_checks, \
        join_validation_results, \
            collect_relationships_issues
from celery import chord
from metadata_validation_conversion.celery import app

def convert_template(file, type):
    errors = []
    if type not in ALLOWED_TEMPLATES:
        errors.append('This type is not supported')
        return {'status': 'Error','error': errors}
    read_excel_file_object = ReadExcelFile(
        file_path=file, json_type=type)
    results = read_excel_file_object.start_conversion()
    if 'Error' in results[0]:
        errors.append(results[0])
        return {'status': 'Error', 'error': errors, 'result': results}
    else:
        if results[2]:
            return {'status': 'Success', 'result': results, 'bovreg_submission': True}
        else:
            return {'status': 'Success', 'result': results, 'bovreg_submission': False}

def validate(conv_result, type):
    json_to_test, structure = conv_result[0], conv_result[1]
    room_id = 'room_id'
    if type == 'samples':
        # Create three tasks that should be run in parallel and assign callback
        task1 = validate_against_schema.s(json_to_test,'samples', structure, room_id=room_id).set(queue='validation')
        task2 = collect_warnings_and_additional_checks.s(json_to_test, 'samples', structure, room_id=room_id).set(queue='validation')
        task3 = collect_relationships_issues.s(json_to_test, structure, room_id=room_id).set(queue='validation')
        join_results = join_validation_results.s(room_id=room_id).set(queue='validation')
        my_chord = chord((task1, task2, task3), join_results)
    else:
        task1 = validate_against_schema.s(json_to_test, type, structure, room_id=room_id).set(queue='validation')
        task2 = collect_warnings_and_additional_checks.s(json_to_test, type, structure, room_id=room_id).set(queue='validation')
        join_results = join_validation_results.s(room_id=room_id).set(queue='validation')
        my_chord = chord((task1, task2), join_results)
    res = my_chord.apply_async()
    validation_result = app.AsyncResult(res.id)
    result = validation_result.get()
    return result