import json
import os

from celery import chord

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from .tasks import prepare_samples_data, prepare_analyses_data, \
    prepare_experiments_data, generate_annotated_template, get_domains, \
    submit_new_domain, submit_to_biosamples, submit_data_to_ena

XLSX_CONTENT_TYPE = 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def get_template(request, task_id, room_id, data_type):
    send_message(annotation_status='Annotating template', room_id=room_id)
    validation_results = app.AsyncResult(task_id)
    json_to_convert = validation_results.get()
    convert_template_task = generate_annotated_template.s(
        json_to_convert, room_id=room_id, data_type=data_type).set(queue='submission')
    res = convert_template_task.apply_async()
    return HttpResponse(json.dumps({'id': res.id}))


def download_template(request, room_id):
    with open(f"/data/{room_id}.xlsx", 'rb') as f:
        file_data = f.read()
    response = HttpResponse(file_data,
                            content_type=f'application/{XLSX_CONTENT_TYPE}')
    response['Content-Disposition'] = 'attachment; filename="annotated.xlsx"'
    os.remove(f"/data/{room_id}.xlsx")
    return response


def download_submission_results(request, submission_type, task_id):
    submission_results = app.AsyncResult(task_id)
    file_to_send = submission_results.get()
    if submission_type == 'samples':
        content_type = 'text/plain'
        filename = 'submission_results.txt'
    elif submission_type == 'experiments' or submission_type == 'analyses':
        content_type = 'text/xml'
        filename = 'submission_results.xml'
    response = HttpResponse(file_to_send, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@csrf_exempt
def domain_actions(request, room_id, domain_action):
    if request.method == 'POST':
        if domain_action == 'choose_domain':
            send_message(submission_message='Waiting: authenticating user',
                         room_id=room_id)
            choose_domain_task = get_domains.s(
                json.loads(request.body.decode('utf-8')), room_id=room_id).set(
                queue='submission')
            res = choose_domain_task.apply_async()
        else:
            send_message(submission_message='Submitting new domain',
                         room_id=room_id)
            submit_new_domain_task = submit_new_domain.s(
                json.loads(request.body.decode('utf-8')), room_id=room_id).set(
                queue='submission')
            res = submit_new_domain_task.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for submission!")


@csrf_exempt
def submit_records(request, action, submission_type, task_id, room_id):
    send_message(submission_message='Preparing data', room_id=room_id)
    if request.method == 'POST':
        request_body = json.loads(request.body.decode('utf-8'))
        if submission_type == 'samples':
            prepare = prepare_samples_data
            submit_task = submit_to_biosamples.s(request_body, room_id=room_id, action=action).set(
                queue='submission')
        elif submission_type == 'experiments':
            prepare = prepare_experiments_data
            submit_task = submit_data_to_ena.s(request_body, room_id=room_id, submission_type='experiments', action=action).set(
                queue='submission')
        elif submission_type == 'analyses':
            prepare = prepare_analyses_data
            submit_task = submit_data_to_ena.s(request_body, room_id=room_id, submission_type='analyses', action=action).set(
                queue='submission')
        else:
            return HttpResponse("Unknown submission type!")

        validation_result = app.AsyncResult(task_id)
        json_to_send = validation_result.get()

        prepare_task = prepare.s(
            json_to_send, room_id=room_id, private=request_body['private_submission'], action=action
        ).set(queue='submission')

        my_chord = chord((prepare_task,), submit_task)
        res = my_chord.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for submission!")
