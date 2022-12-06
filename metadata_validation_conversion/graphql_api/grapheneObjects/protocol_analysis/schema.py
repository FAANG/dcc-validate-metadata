from graphene import InputObjectType, ObjectType, String, Field, ID, relay, List
from graphene.relay import Connection, Node
from graphql_api.tasks import resolve_all_task
from celery.result import AsyncResult
from ..helpers import fetch_index_records, fetch_with_join
from .fieldObjects import AnalysesField, ProtocolAnalysisJoinField
from .arguments.filter import ProtocolAnalysisFilterArgument
from ..commonFieldObjects import TaskResponse


def fetch_single_protocol_analysis(args):
    q = ''

    if args['id']:
        q = [{"terms": {"key": [args['id']]}}]
    elif args['alternate_id']:
        q = [{"terms": {"alternateId": [args['alternate_id']]}}]

    res = fetch_index_records('protocol_analysis', filter=q)[0]
    res['id'] = res['key']
    return res


class ProtocolAnalysisNode(ObjectType):
    class Meta:
        interfaces = (Node,)

    universityName = String()
    protocolDate = String()
    protocolName = String()
    key = String()
    url = String()
    analyses = List(of_type=AnalysesField)
    join = Field(ProtocolAnalysisJoinField)

    @classmethod
    def get_node(cls, info, id):
        return fetch_single_protocol_analysis({'id': id})


class ProtocolAnalysisConnection(Connection):
    class Meta:
        node = ProtocolAnalysisNode

    class Edge:
        pass


class ProtocolAnalysisSchema(ObjectType):
    protocol_analysis = Field(ProtocolAnalysisNode, id=ID(required=True), alternate_id=ID(required=False))
    all_protocol_analysis = relay.ConnectionField(ProtocolAnalysisConnection, filter=ProtocolAnalysisFilterArgument())

    all_protocol_analysis_as_task = Field(TaskResponse, filter=ProtocolAnalysisFilterArgument())
    all_protocol_analysis_task_result = relay.ConnectionField(ProtocolAnalysisConnection, task_id=String())
    # just an example of relay.connection field and batch loader
    some_protocol_analysis = relay.ConnectionField(ProtocolAnalysisConnection, ids=List(of_type=String, required=True))

    def resolve_protocol_analysis(root, info, **args):
        return fetch_single_protocol_analysis(args)

    def resolve_all_protocol_analysis(root, info, **kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'protocol_analysis')
        return res

    def resolve_all_protocol_analysis_as_task(root, info, **kwargs):
        task = resolve_all_task.apply_async(args=[kwargs, 'protocol_analysis'], queue='graphql_api')
        response = {'id': task.id, 'status': task.status, 'result': task.result}
        return response

    def resolve_all_protocol_analysis_task_result(root, info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []
