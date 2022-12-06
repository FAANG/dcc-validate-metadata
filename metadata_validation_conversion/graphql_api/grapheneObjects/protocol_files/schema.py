from graphene import InputObjectType, ObjectType, String, Field, ID, relay, List
from graphene.relay import Connection, Node
from graphql_api.tasks import resolve_all_task
from celery.result import AsyncResult
from ..helpers import fetch_index_records, fetch_with_join
from .fieldObjects import ExperimentsField, ProtocolFilesJoinField
from .arguments.filter import ProtocolFilesFilterArgument
from ..commonFieldObjects import TaskResponse


def fetch_single_protocol_file(args):
    q = ''

    if args['id']:
        q = [{"terms": {"key": [args['id']]}}]
    elif args['alternate_id']:
        q = [{"terms": {"alternateId": [args['alternate_id']]}}]

    res = fetch_index_records('protocol_files', filter=q)[0]
    res['id'] = res['key']
    return res


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

    @classmethod
    def get_node(cls, info, id):
        return fetch_single_protocol_file({'id': id})


class ProtocolFilesConnection(Connection):
    class Meta:
        node = ProtocolFilesNode

    class Edge:
        pass


class ProtocolFilesSchema(ObjectType):
    protocol_file = Field(ProtocolFilesNode, id=ID(required=True), alternate_id=ID(required=False))
    all_protocol_files = relay.ConnectionField(ProtocolFilesConnection, filter=ProtocolFilesFilterArgument())

    all_protocol_files_as_task = Field(TaskResponse, filter=ProtocolFilesFilterArgument())
    all_protocol_files_task_result = relay.ConnectionField(ProtocolFilesConnection, task_id=String())
    # just an example of relay.connection field and batch loader
    some_protocol_files = relay.ConnectionField(ProtocolFilesConnection, ids=List(of_type=String, required=True))

    def resolve_protocol_file(root, info, **args):
        return fetch_single_protocol_file(args)

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

