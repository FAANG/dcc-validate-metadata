from graphene import ObjectType, String, Field, ID, relay, List
from graphene.relay import Connection, Node
from graphql_api.tasks import launch_celery_task
from celery.result import AsyncResult
from ..helpers import fetch_index_records, fetch_with_join
from .field_objects import DatasetJoinField, DatasetExperimentField, FileField, DatasetPublishedArticlesField, \
    SpecimenField
from .arguments.filter import DatasetFilterArgument
from ..common_field_objects import OntologyField, TaskResponse


def fetch_single_dataset(args):
    q = ''

    if args['id']:
        q = [{"terms": {"accession": [args['id']]}}]
    elif args['alternate_id']:
        q = [{"terms": {"alternateId": [args['alternate_id']]}}]

    res = fetch_index_records('dataset', filter=q)[0]
    res['id'] = res['accession']
    return res


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

    @classmethod
    def get_node(cls, info, id):
        return fetch_single_dataset({'id': id})


class DatasetConnection(Connection):
    class Meta:
        node = DatasetNode

    class Edge:
        pass


class DatasetSchema(ObjectType):
    dataset = Field(DatasetNode, id=ID(required=True), alternate_id=ID(required=False))
    all_datasets = relay.ConnectionField(DatasetConnection, filter=DatasetFilterArgument())
    all_datasets_as_task = Field(TaskResponse, filter=DatasetFilterArgument())
    all_datasets_task_result = relay.ConnectionField(DatasetConnection, task_id=String())

    def resolve_dataset(root, info, **args):
        return fetch_single_dataset(args)

    def resolve_all_datasets(root, info, **kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'dataset')
        return res

    def resolve_all_datasets_as_task(root, info, **kwargs):
        task = launch_celery_task.apply_async(args=[kwargs, 'dataset'], queue='graphql_api')
        response = {'id': task.id, 'status': task.status, 'result': task.result}
        return response

    def resolve_all_datasets_task_result(root, info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []

