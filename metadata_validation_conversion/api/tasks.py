from abc import ABC
from celery import Task
from metadata_validation_conversion.celery import app
from elasticsearch import Elasticsearch
from elasticsearch import RequestsHttpConnection
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


class CeleryTask(Task, ABC):
    abstract = True


@app.task(bind=True, base=CeleryTask)
def es_search_task(self, index, key_args):
    key_args['index'] = index

    es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection,
                       http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=True)

    if key_args['req_body']:
        data = es.search(
            index=key_args['index'],
            body=json.loads(key_args['req_body'].decode("utf-8"), track_total_hits=key_args['track_total_hits'])
        )
    else:
        data = es.search(
            index=key_args['index'], body=key_args['body'], track_total_hits=key_args['track_total_hits']
        )
    index = index.replace(
        'protocol_files', 'protocol/experiments'
    ).replace(
        'protocol_analysis', 'protocol/analysis'
    ).replace('protocol_samples', 'protocol/samples')
    data['index'] = index

    return data
