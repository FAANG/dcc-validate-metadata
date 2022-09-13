from metadata_validation_conversion.constants import ALLOWED_TEMPLATES
from metadata_validation_conversion.celery import app
from conversion.ReadExcelFile import ReadExcelFile
from validation.tasks import validate_against_schema, \
    collect_warnings_and_additional_checks, \
        join_validation_results, \
            collect_relationships_issues
from submission.tasks import generate_annotated_template, \
            prepare_samples_data, prepare_analyses_data, prepare_experiments_data, \
                submit_to_biosamples, submit_data_to_ena
from submission.helpers import get_credentials
from submission.BiosamplesSubmission import BioSamplesSubmission
from celery import chord
import os

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

def validate(conv_result, type, annotate_template):
    json_to_test, structure = conv_result[0], conv_result[1]
    room_id = 'room'
    if type == 'samples':
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
    if annotate_template == 'true':
        generate_template_task = generate_annotated_template.s(
            result, room_id=room_id, data_type=type).set(queue='validation')
        res = generate_template_task.apply_async()
        annotation_result = app.AsyncResult(res.id)
        result = annotation_result.get()
        with open(f"/data/{room_id}.xlsx", 'rb') as f:
            file_data = f.read()
        os.remove(f"/data/{room_id}.xlsx")
        return file_data
    return result

def domain_tasks(data, domain_action):
    username, password = get_credentials(data)
    biosamples_submission = BioSamplesSubmission(username, password, {},
                                                 data['mode'])
    if domain_action == 'choose_domain':
        results = biosamples_submission.choose_domain()
        if 'Error' not in results:
            return {"domains": results}
    else:
        results = biosamples_submission.create_domain(
            data['domain_name'], data['domain_description'])
        if 'Error' not in results:
            results = biosamples_submission.choose_domain()
            return {"domains": results}
    return results

def submit_data(conversion_result, data, type):
    room_id = 'room'
    if type == 'samples':
        prepare = prepare_samples_data
        submit = submit_to_biosamples
        submit_task = submit.s(data, room_id=room_id).set(
            queue='submission')
    elif type == 'experiments':
        prepare = prepare_experiments_data
        submit = submit_data_to_ena
        submit_task = submit.s(data, room_id=room_id, submission_type='experiments').set(
            queue='submission')
    elif type == 'analyses':
        prepare = prepare_analyses_data
        submit = submit_data_to_ena
        submit_task = submit.s(data, room_id=room_id, submission_type='analyses').set(
            queue='submission')
    else:
        return "Unknown submission type!"
    prepare_task = prepare.s(
        conversion_result, room_id=room_id, private=data['private_submission']
    ).set(queue='submission')
    my_chord = chord((prepare_task,), submit_task)
    res = my_chord.apply_async()
    submission_results = app.AsyncResult(res.id)
    file_to_send = submission_results.get()
    if type == 'samples':
        content_type = 'text/plain'
        filename = 'submission_results.txt'
    elif type == 'experiments' or type == 'analyses':
        content_type = 'text/xml'
        filename = 'submission_results.xml'
    return file_to_send, filename, content_type