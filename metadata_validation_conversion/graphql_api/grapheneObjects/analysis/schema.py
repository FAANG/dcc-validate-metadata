from graphene import ObjectType, String, Field, ID, relay, List
from graphene.relay import Connection, Node
from graphql_api.tasks import resolve_all_task
from celery.result import AsyncResult
from ..helpers import fetch_with_join
from .fieldObjects import AnalysisDateField, AnalysisJoinField, FilesField, AnalysisOrganismField
from .arguments.filter import AnalysisFilterArgument
from ..commonFieldObjects import ProtocolField, TaskResponse


class AnalysisNode(ObjectType):
    class Meta:
        interfaces = (Node,)

    accession = String()
    project = String()
    secondaryProject = String()
    title = String()
    alias = String()
    description = String()
    standardMet = String()
    versionLastStandardMet = String()
    releaseDate = String()
    updateDate = String()
    organism = Field(AnalysisOrganismField)
    type = String()
    datasetAccession = String()
    datasetInPortal = String()
    sampleAccessions = List(String)
    experimentAccessions = List(String)
    runAccessions = List(String)
    analysisAccessions = List(String)
    files = List(of_type=FilesField)
    analysisDate = Field(AnalysisDateField)
    assayType = String()
    analysisProtocol = Field(ProtocolField)
    analysisType = String()
    referenceGenome = String()
    analysisCenter = String()
    analysisCodeRepository = String()
    experimentType = List(String)
    program = String()
    platform = List(String)
    imputation = String()
    join = Field(AnalysisJoinField)


class AnalysisConnection(Connection):
    class Meta:
        node = AnalysisNode

    class Edge:
        pass


class AnalysisSchema(ObjectType):
    all_analysis = relay.ConnectionField(AnalysisConnection, filter=AnalysisFilterArgument())
    all_analysis_as_task = Field(TaskResponse, filter=AnalysisFilterArgument())
    all_analysis_task_result = relay.ConnectionField(AnalysisConnection, task_id=String())

    def resolve_all_analysis(root, info, **kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'analysis')
        return res

    def resolve_all_analysis_as_task(root, info, **kwargs):
        task = resolve_all_task.apply_async(args=[kwargs, 'analysis'], queue='graphql_api')
        response = {'id': task.id, 'status': task.status, 'result': task.result}
        return response

    def resolve_all_analysis_task_result(root, info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []

