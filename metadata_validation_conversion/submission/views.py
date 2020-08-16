import json
import os

from celery import chord

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from .tasks import prepare_samples_data, prepare_analyses_data, \
    prepare_experiments_data, generate_annotated_template, get_domains, \
    submit_new_domain, submit_to_biosamples, submit_experiments_to_ena
from .helpers import zip_files

XLSX_CONTENT_TYPE = 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def get_template(request, task_id, room_id, data_type):
    send_message(annotation_status='Annotating template', room_id=room_id)
    validation_results = app.AsyncResult(task_id)
    json_to_convert = validation_results.get()
    convert_template_task = generate_annotated_template.s(
        json_to_convert, room_id, data_type).set(queue='submission')
    res = convert_template_task.apply_async()
    return HttpResponse(json.dumps({'id': res.id}))


def download_template(request, room_id):
    with open(f"{room_id}.xlsx", 'rb') as f:
        file_data = f.read()
    response = HttpResponse(file_data,
                            content_type=f'application/{XLSX_CONTENT_TYPE}')
    response['Content-Disposition'] = 'attachment; filename="annotated.xlsx"'
    print('removing file')
    os.remove(f"{room_id}.xlsx")
    return response


def download_submission_results(request, submission_type, task_id):
    submission_results = app.AsyncResult(task_id)
    file_to_send = submission_results.get()
    if submission_type == 'samples':
        content_type = 'text/plain'
        filename = 'submission_results.txt'
    elif submission_type == 'experiments':
        content_type = 'text/xml'
        filename = 'submission_results.xml'
    response = HttpResponse(file_to_send, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def samples_conversion(request, task_id, room_id):
    send_message(submission_status='Preparing data', room_id=room_id)
    validation_result = app.AsyncResult(task_id)
    json_to_send = validation_result.get()
    prepare_samples_data_task = prepare_samples_data.s(
        json_to_send, room_id).set(queue='submission')
    res = prepare_samples_data_task.apply_async()
    return HttpResponse(json.dumps({"id": res.id}))


@csrf_exempt
def choose_domain(request, room_id):
    send_message(submission_message='Waiting: authenticating user',
                 room_id=room_id)
    if request.method == 'POST':
        choose_domain_task = get_domains.s(
            json.loads(request.body.decode('utf-8')), room_id).set(
            queue='submission')
        res = choose_domain_task.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for submission!")


@csrf_exempt
def submit_domain(request, room_id):
    send_message(submission_message='Submitting new domain', room_id=room_id)
    if request.method == 'POST':
        submit_new_domain_task = submit_new_domain.s(
            json.loads(request.body.decode('utf-8')), room_id).set(
            queue='submission')
        res = submit_new_domain_task.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for submission!")


@csrf_exempt
def submit_records(request, room_id, task_id):
    send_message(submission_message='Preparing data', room_id=room_id)
    if request.method == 'POST':
        validation_result = app.AsyncResult(task_id)
        json_to_send = validation_result.get()
        prepare_samples_data_task = prepare_samples_data.s(
            json_to_send, room_id).set(queue='submission')
        submit_to_biosamples_task = submit_to_biosamples.s(
            json.loads(request.body.decode('utf-8')), room_id).set(
            queue='submission')
        my_chord = chord((prepare_samples_data_task,),
                         submit_to_biosamples_task)
        res = my_chord.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for submission!")


@csrf_exempt
def experiments_submission(request, task_id, room_id):
    send_message(submission_message='Preparing data', room_id=room_id)
    if request.method == 'POST':
        validation_result = app.AsyncResult(task_id)
        json_to_send = validation_result.get()
        prepare_experiments_data_task = prepare_experiments_data.s(
            json_to_send, room_id).set(queue='submission')
        submit_experiments_to_ena_task = submit_experiments_to_ena.s(
            json.loads(request.body.decode('utf-8')), room_id).set(
            queue='submission')
        my_chord = chord((prepare_experiments_data_task,),
                         submit_experiments_to_ena_task)
        res = my_chord.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for submission!")


def analyses_submission(request, task_id, room_id):
    send_message(submission_status='Preparing data', room_id=room_id)
    validation_result = app.AsyncResult(task_id)
    json_to_send = validation_result.get()
    prepare_analyses_data_task = prepare_analyses_data.s(
        json_to_send, room_id).set(queue='submission')
    res = prepare_analyses_data_task.apply_async()
    return HttpResponse(json.dumps({"id": res.id}))


def send_data(request, task_id):
    conversion_results = app.AsyncResult(task_id)
    data_to_send = conversion_results.get()
    if isinstance(data_to_send, list) and data_to_send[0] in ['analysis',
                                                              'experiment']:
        if data_to_send[0] == 'analysis':
            filename = 'analyses.zip'
        else:
            filename = 'experiments.zip'
        zipped_file = zip_files(data_to_send[1:], data_to_send[0])
        response = HttpResponse(zipped_file,
                                content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    else:
        response = HttpResponse(json.dumps(data_to_send),
                                content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="samples.json"'
    return response
