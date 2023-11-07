from abc import ABC
from celery import Task
import channels.layers
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message_gsearch
from elasticsearch import Elasticsearch
from elasticsearch import RequestsHttpConnection
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

channel_layer = channels.layers.get_channel_layer()


class CeleryTask(Task, ABC):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        send_message_gsearch(task_id, status='Error', errors=f'Current error is: {exc}')

    def on_success(self, retval, task_id, args, kwargs):
        send_message_gsearch(task_id, status='Success')


@app.task(bind=True, base=CeleryTask)
def es_search_task(self, req_body, index, body, track_total_hits, from_=None, _source=None, sort=None):
    logging.debug(index)
    logging.debug(body)
    logging.debug(self.request.id)

    es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection,
                       http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=True)

    send_message_gsearch(self.request.id, gsearch_status='task_received')
    if req_body:
        data = es.search(index=index, body=json.loads(req_body.decode("utf-8"), track_total_hits=track_total_hits))
    else:
        data = es.search(
            index=index, from_=from_, _source=_source, sort=sort, body=body, track_total_hits=track_total_hits
        )
    send_message_gsearch(self.request.id, gsearch_status='task_finished')

    return data
