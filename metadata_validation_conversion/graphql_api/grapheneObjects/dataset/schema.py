from graphene import ObjectType, String, Field, ID, relay, List
from graphene.relay import Connection, Node
from graphql_api.tasks import resolve_all_task
from celery.result import AsyncResult
from ..helpers import fetch_with_join
from .fieldObjects import DatasetJoinField, DatasetExperimentField, FileField, DatasetPublishedArticlesField, \
    SpecimenField
from .arguments.filter import DatasetFilterArgument
from ..commonFieldObjects import OntologyField, TaskResponse


class DatasetNode(ObjectType):
    class Meta:
        interfaces = (Node,)

    accession = String()
    standardMet = String()
    secondaryProject = List(String)
    title = String()
    alias = String()
    assayType = List(String)
    tech = List(String)
    secondaryAccession = String()
    archive = List(String)
    specimen = List(of_type=SpecimenField)
    species = List(of_type=OntologyField)
    releaseDate = String()
    updateDate = String()
    file = List(of_type=FileField)
    experiment = List(of_type=DatasetExperimentField)
    instrument = List(String)
    centerName = List(String)
    paperPublished = String()
    publishedArticles = List(of_type=DatasetPublishedArticlesField)
    submitterEmail = String()
    join = Field(DatasetJoinField)


class DatasetConnection(Connection):
    class Meta:
        node = DatasetNode

    class Edge:
        pass


class DatasetSchema(ObjectType):
    all_datasets = relay.ConnectionField(DatasetConnection, filter=DatasetFilterArgument())
    all_datasets_as_task = Field(TaskResponse, filter=DatasetFilterArgument())
    all_datasets_task_result = relay.ConnectionField(DatasetConnection, task_id=String())

    def resolve_all_datasets(root, info, **kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'dataset')
        return res

    def resolve_all_datasets_as_task(root, info, **kwargs):
        task = resolve_all_task.apply_async(args=[kwargs, 'dataset'], queue='graphql_api')
        response = {'id': task.id, 'status': task.status, 'result': task.result}
        return response

    def resolve_all_datasets_task_result(root, info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []


