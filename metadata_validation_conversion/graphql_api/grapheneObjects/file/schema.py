from graphene import InputObjectType, ObjectType, String, Field, ID, relay, List
from graphene.relay import Connection, Node
from graphql_api.tasks import resolve_all_task
from celery.result import AsyncResult
from ..helpers import fetch_index_records, fetch_with_join
from .fieldObjects import FileExperimentField, FileJoinField, FilePublishedArticlesField, RunField, SpeciesField, \
    StudyField
from .arguments.filter import FileFilterArgument
from ..commonFieldObjects import TaskResponse


def fetch_single_file(args):
    q = ''

    if args['id']:
        q = [{"terms": {"_id": [args['id']]}}]
    elif args['alternate_id']:
        q = [{"terms": {"alternateId": [args['alternate_id']]}}]

    res = fetch_index_records('file', filter=q)[0]

    res['id'] = res['name'].split('.', 1)[0]
    return res


class FileNode(ObjectType):
    class Meta:
        interfaces = (Node,)

    specimen = String()
    organism = String()
    species = Field(SpeciesField)
    url = String()
    name = String()
    secondaryProject = String()
    type = String()
    size = String()
    readableSize = String()
    checksum = String()
    checksumMethod = String()
    archive = String()
    readCount = String()
    baseCount = String()
    releaseDate = String()
    updateDate = String()
    submission = String()
    experiment = Field(FileExperimentField)
    study = Field(StudyField)
    run = Field(RunField)
    paperPublished = String()
    publishedArticles = List(of_type=FilePublishedArticlesField)
    submitterEmail = String()
    join = Field(FileJoinField)

    @classmethod
    def get_node(cls, info, id):
        args = {'id': id}
        return fetch_single_file(args)


class FileConnection(Connection):
    class Meta:
        node = FileNode

    class Edge:
        pass


class FileSchema(ObjectType):
    file = Field(FileNode, id=ID(required=True), alternate_id=ID(required=False))
    all_files = relay.ConnectionField(FileConnection, filter=FileFilterArgument())

    all_files_as_task = Field(TaskResponse, filter=FileFilterArgument())
    all_files_task_result = relay.ConnectionField(FileConnection, task_id=String())
    # just an example of relay.connection field and batch loader
    some_files = relay.ConnectionField(FileConnection, ids=List(of_type=String, required=True))

    def resolve_file(root, info, **args):
        return fetch_single_file(args)

    def resolve_all_files(root, info, **kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'file')
        return res

    def resolve_all_files_as_task(root, info, **kwargs):
        task = resolve_all_task.apply_async(args=[kwargs, 'file'], queue='graphql_api')
        response = {'id': task.id, 'status': task.status, 'result': task.result}
        return response

    def resolve_all_files_task_result(root, info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []

