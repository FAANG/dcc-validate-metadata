import json
import os

from celery import chord

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from elasticsearch import Elasticsearch, RequestsHttpConnection
from django.conf import settings
from django.core.mail import send_mail
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from .tasks import prepare_samples_data, prepare_analyses_data, \
    prepare_experiments_data, generate_annotated_template, submit_to_biosamples, submit_data_to_ena, send_user_email

XLSX_CONTENT_TYPE = 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'

es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection,
                   http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=True)


def get_template(request, task_id, room_id, data_type, action):
    send_message(annotation_status='Annotating template', room_id=room_id)
    validation_results = app.AsyncResult(task_id)
    json_to_convert = validation_results.get()
    convert_template_task = generate_annotated_template.s(
        json_to_convert, room_id=room_id, data_type=data_type, action=action).set(queue='submission')
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

        # mode is required for samples data
        if submission_type == 'samples':
            prepare_task = prepare.s(
                json_to_send, room_id=room_id, private=request_body['private_submission'], action=action,
                mode=request_body['mode']).set(queue='submission')
        else:
            prepare_task = prepare.s(
                json_to_send, room_id=room_id, private=request_body['private_submission'], action=action)\
                .set(queue='submission')

        my_chord = chord((prepare_task,), submit_task)
        res = my_chord.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for submission!")


@csrf_exempt
def filtered_subscription(request, index_name, index_pk, subscriber_email):
    filters = request.GET.get('filters', '{}')
    filters_dict = json.loads(filters)
    es_records = fetch_filtered_data(filters_dict, index_name)

    if len(es_records) > 0:
        subscription_count = 0
        record_ids = []
        for rec in es_records:
            # add _id to record
            _id = rec['_id'] if '_id' in rec else ''
            submission_recordset = rec['_source']
            submission_recordset['_id'] = _id

            record_ids.append(rec["_source"][index_pk])

            if 'subscribers' in submission_recordset:
                existing_emails = [ele['email'] for ele in submission_recordset['subscribers']]
                if subscriber_email in existing_emails:
                    if len(es_records) == 1:
                        send_message(
                            submission_message=f'{subscriber_email} has already been registered to receive updates '
                                               f'about record '
                                               f'{rec["_source"][index_pk]}.',
                            subscription_status='warning',
                            room_id=f'subscription_{index_name}')
                        return HttpResponse(status=200)

                    subscription_count += 1
                    continue
                submission_recordset['subscribers'].append({'email': subscriber_email})
            else:
                submission_recordset.update({'subscribers': [{'email': subscriber_email}]})

            update_payload = {"doc": {"subscribers": submission_recordset['subscribers']}}
            res = es.update(index=index_name, id=submission_recordset[index_pk], body=update_payload)

            if res['result'] == 'updated':
                subscription_count += 1

        if subscription_count > 0:
            send_message(submission_message=f'{subscriber_email} has successfully been registered to receive '
                                            f'updates for the selected record(s)',
                         subscription_status='success',
                         room_id=f'subscription_{index_name}')
            return HttpResponse(status=200)
    return HttpResponse(status=404)


@csrf_exempt
def submission_unsubscribe(request, study_id, subscriber_email):
    filters = {'query': {'bool': {'filter': [{'terms': {'study_id': [f'{study_id}']}}]}}}
    query = json.dumps(filters)
    data = es.search(index='submissions', size=1, from_=0, track_total_hits=True, body=json.loads(query))

    if len(data['hits']['hits']) > 0 and data['hits']['hits'][0]['_source']:
        submission_recordset = data['hits']['hits'][0]['_source']
        if 'subscribers' in submission_recordset:
            existing_emails = [ele['email'] for ele in submission_recordset['subscribers']]
            print(existing_emails)
            if subscriber_email in existing_emails:
                updated_list = [ele for ele in submission_recordset['subscribers']
                                if not (ele['email'] == subscriber_email)]
                update_payload = {"doc": {"subscribers": updated_list}}
                res = es.update(index="submissions", id=study_id, body=update_payload)
                if res['result'] == 'updated':
                    send_mail(
                        f'You have been unsubscribed from study {study_id}',
                        f'You will no longer receive updates about submission {study_id}.',
                        'faang-dcc@ebi.ac.uk',
                        [subscriber_email],
                        fail_silently=False,
                    )
                    return HttpResponse(status=200)
    return HttpResponse(status=404)


@csrf_exempt
def subscription_email(request, study_id, subscriber_email):
    return send_user_email(study_id, subscriber_email)


def fetch_filtered_data(filters, index):
    # generate query for filtering
    filter_values = []
    not_filter_values = []
    body = {}

    for key in filters.keys():
        if filters[key][0] != 'false':
            filter_values.append({"terms": {key: filters[key]}})
        else:
            not_filter_values.append({"match": {key: "true"}})
    filter_val = {}
    if filter_values:
        filter_val['must'] = filter_values
    if not_filter_values:
        filter_val['must_not'] = not_filter_values
    if filter_val:
        body['query'] = {'bool': filter_val}

    count = 0
    recordset = []
    while True:
        res = es.search(index=index, size=50000, from_=count,
                        track_total_hits=True, body=body)
        count += 50000
        records = res['hits']['hits']
        recordset += records
        if count > res['hits']['total']['value']:
            break
    return recordset


