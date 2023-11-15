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


@app.task(bind=True, base=CeleryTask)
def es_search_task(self, index, key_args):
    key_args['index'] = index

    es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection,
                       http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=True)

    send_message_gsearch(self.request.id, gsearch_status='task_received')

    if key_args['req_body']:
        data = es.search(
            index=key_args['index'],
            body=json.loads(key_args['req_body'].decode("utf-8"), track_total_hits=key_args['track_total_hits'])
        )
    else:
        data = es.search(
            index=key_args['index'], from_=key_args['from_'], _source=key_args['_source'],
            sort=key_args['sort'], body=key_args['body'], track_total_hits=key_args['track_total_hits']
        )
    data['index'] = index

    send_message_gsearch(self.request.id, gsearch_status='task_finished')

    return data
