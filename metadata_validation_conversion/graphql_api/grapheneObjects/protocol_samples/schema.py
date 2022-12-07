from graphene import ObjectType, String, Field, ID, relay, List
from graphene.relay import Connection, Node
from graphql_api.tasks import resolve_all_task
from celery.result import AsyncResult
from ..helpers import fetch_with_join
from .fieldObjects import ProtocolSamplesJoinField, SpecimensField
from .arguments.filter import ProtocolSamplesFilterArgument
from ..commonFieldObjects import TaskResponse


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


class ProtocolSamplesConnection(Connection):
    class Meta:
        node = ProtocolSamplesNode

    class Edge:
        pass


class ProtocolSamplesSchema(ObjectType):
    all_protocol_samples = relay.ConnectionField(ProtocolSamplesConnection, filter=ProtocolSamplesFilterArgument())
    all_protcol_samples_as_task = Field(TaskResponse, filter=ProtocolSamplesFilterArgument())
    all_protcol_samples_task_result = relay.ConnectionField(ProtocolSamplesConnection, task_id=String())

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

