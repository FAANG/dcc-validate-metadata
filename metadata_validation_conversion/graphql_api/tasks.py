from abc import ABC
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message_graphql
from graphql_api.grapheneObjects.helpers import fetch_with_join
from celery import Task
import channels.layers

channel_layer = channels.layers.get_channel_layer()


class CeleryTask(Task, ABC):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print(exc)
        send_message_graphql(task_id, graphql_status='Error',
                             errors=f'There is a problem with the graphql api. Error: {exc}')

    def on_success(self, retval, task_id, args, kwargs):
        send_message_graphql(task_id, graphql_status='Success')


@app.task(bind=True, base=CeleryTask)
def launch_celery_task(self, kwargs, left_index):
    send_message_graphql(self.request.id, graphql_status='task_received')
    filter_query = kwargs['filter'] if 'filter' in kwargs else {}
    res = fetch_with_join(filter_query, left_index)
    send_message_graphql(self.request.id, graphql_status='task_finished')
    return res
