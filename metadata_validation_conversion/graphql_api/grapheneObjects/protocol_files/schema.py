from graphene import ObjectType, String, Field, ID, relay, List
from graphene.relay import Connection, Node
from graphql_api.tasks import resolve_all_task
from celery.result import AsyncResult
from ..helpers import fetch_with_join
from .fieldObjects import ExperimentsField, ProtocolFilesJoinField
from .arguments.filter import ProtocolFilesFilterArgument
from ..commonFieldObjects import TaskResponse


class ProtocolFilesNode(ObjectType):
    class Meta:
        interfaces = (Node,)

    name = String()
    experimentTarget = String()
    assayType = String()
    key = String()
    url = String()
    filename = String()
    experiments = List(of_type=ExperimentsField)
    join = Field(ProtocolFilesJoinField)


class ProtocolFilesConnection(Connection):
    class Meta:
        node = ProtocolFilesNode

    class Edge:
        pass


class ProtocolFilesSchema(ObjectType):
    all_protocol_files = relay.ConnectionField(ProtocolFilesConnection, filter=ProtocolFilesFilterArgument())
    all_protocol_files_as_task = Field(TaskResponse, filter=ProtocolFilesFilterArgument())
    all_protocol_files_task_result = relay.ConnectionField(ProtocolFilesConnection, task_id=String())

    def resolve_all_protocol_files(root, info, **kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'protocol_files')
        return res

    def resolve_all_protocol_files_as_task(root, info, **kwargs):
        task = resolve_all_task.apply_async(args=[kwargs, 'protocol_files'], queue='graphql_api')
        response = {'id': task.id, 'status': task.status, 'result': task.result}
        return response

    def resolve_all_protocol_files_task_result(root, info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []

