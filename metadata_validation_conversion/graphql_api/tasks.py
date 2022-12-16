from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message, send_message_graphql
from metadata_validation_conversion.constants import ALLOWED_TEMPLATES
from graphql_api.grapheneObjects.helpers import fetch_with_join

from celery import Task
from celery.utils.log import get_task_logger
from celery.signals import after_setup_logger
import logging
import os.path
import time
import channels.layers

channel_layer = channels.layers.get_channel_layer()

APP_PATH = os.path.dirname(os.path.realpath(__file__))
logger = get_task_logger(__name__)


class LogErrorsTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print(exc)
        # send_message(room_id=args[0], conversion_status='Error',
        #              errors=f'There is a problem with the graphql api. Error: {exc}')


class CallbackTask(LogErrorsTask):
    def on_success(self, retval, task_id, args, kwargs):
        send_message_graphql(task_id, 'task finished')


@app.task(bind=True, base=CallbackTask)
def resolve_all_task(self, kwargs, left_index):
    time.sleep(2)
    send_message_graphql(self.request.id, 'task received')
    filter_query = kwargs['filter'] if 'filter' in kwargs else {}
    res = fetch_with_join(filter_query, left_index)
    # res = {'data':[{'biosampleId':'SAMEA1','name':'O1'},{'biosampleId':'SAMEA2','name':'O2'}]}
    send_message_graphql(self.request.id, 'task about to finish')

    return res
