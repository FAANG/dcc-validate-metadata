from graphene import InputObjectType, ObjectType, String, Field, ID, relay, List
from graphene.relay import Connection, Node
from graphql_api.tasks import resolve_all_task
from celery.result import AsyncResult
from ..helpers import fetch_index_records, fetch_with_join
from .fieldObjects import ProtocolSamplesJoinField, SpecimensField
from .arguments.filter import ProtocolSamplesFilterArgument
from ..commonFieldObjects import TaskResponse


def fetch_single_protocol_sample(args):
    q = ''

    if args['id']:
        q = [{"terms": {"key": [args['id']]}}]
    elif args['alternate_id']:
        q = [{"terms": {"alternateId": [args['alternate_id']]}}]

    res = fetch_index_records('protocol_samples', filter=q)[0]
    res['id'] = res['key']
    return res


class ProtocolSamplesNode(ObjectType):
    class Meta:
        interfaces = (Node,)

    universityName = String()
    protocolDate = String()
    protocolName = String()
    key = String()
    url = String()
    specimens = List(of_type=SpecimensField)
    join = Field(ProtocolSamplesJoinField)

    @classmethod
    def get_node(cls, info, id):
        return fetch_single_protocol_sample({'id': id})


class ProtocolSamplesConnection(Connection):
    class Meta:
        node = ProtocolSamplesNode

    class Edge:
        pass


class ProtocolSamplesSchema(ObjectType):
    protocol_sample = Field(ProtocolSamplesNode, id=ID(required=True), alternate_id=ID(required=False))
    all_protocol_samples = relay.ConnectionField(ProtocolSamplesConnection, filter=ProtocolSamplesFilterArgument())

    all_protcol_samples_as_task = Field(TaskResponse, filter=ProtocolSamplesFilterArgument())
    all_protcol_samples_task_result = relay.ConnectionField(ProtocolSamplesConnection, task_id=String())
    # just an example of relay.connection field and batch loader
    some_protocol_samples = relay.ConnectionField(ProtocolSamplesConnection, ids=List(of_type=String, required=True))

    def resolve_protocol_sample(root, info, **args):
        return fetch_single_protocol_sample(args)

    def resolve_all_protocol_samples(root, info, **kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'protocol_samples')
        return res

    def resolve_all_protcol_samples_as_task(root, info, **kwargs):
        task = resolve_all_task.apply_async(args=[kwargs, 'protocol_samples'], queue='graphql_api')
        response = {'id': task.id, 'status': task.status, 'result': task.result}
        return response

    def resolve_all_protcol_samples_task_result(root, info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []

