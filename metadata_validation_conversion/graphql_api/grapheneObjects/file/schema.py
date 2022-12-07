from graphene import ObjectType, String, Field, ID, relay, List
from graphene.relay import Connection, Node
from graphql_api.tasks import resolve_all_task
from celery.result import AsyncResult
from ..helpers import fetch_with_join
from .fieldObjects import FileExperimentField, FileJoinField, FilePublishedArticlesField, RunField, SpeciesField, \
    StudyField
from .arguments.filter import FileFilterArgument
from ..commonFieldObjects import TaskResponse


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


class FileConnection(Connection):
    class Meta:
        node = FileNode

    class Edge:
        pass


class FileSchema(ObjectType):
    all_files = relay.ConnectionField(FileConnection, filter=FileFilterArgument())
    all_files_as_task = Field(TaskResponse, filter=FileFilterArgument())
    all_files_task_result = relay.ConnectionField(FileConnection, task_id=String())

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

