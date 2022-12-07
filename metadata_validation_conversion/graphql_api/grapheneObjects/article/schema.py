from graphene import ObjectType, String, Field, relay, List
from graphene.relay import Connection, Node
from graphql_api.tasks import resolve_all_task
from celery.result import AsyncResult
from ..helpers import fetch_with_join
from .fieldObjects import RelatedDatasets_Field, ArticleJoin_Field
from .arguments.filter import ArticleFilterArgument
from ..commonFieldObjects import TaskResponse


class ArticleNode(ObjectType):
    class Meta:
        interfaces = (Node,)

    pmcId = String()
    pubmedId = String()
    doi = String()
    title = String()
    authorString = String()
    journal = String()
    issue = String()
    volume = String()
    year = String()
    pages = String()
    isOpenAccess = String()
    datasetSource = String()
    relatedDatasets = List(of_type=RelatedDatasets_Field)
    secondaryProject = List(String)
    join = Field(ArticleJoin_Field)


class ArticleConnection(Connection):
    class Meta:
        node = ArticleNode

    class Edge:
        pass


class ArticleSchema(ObjectType):
    all_articles = relay.ConnectionField(ArticleConnection, filter=ArticleFilterArgument())
    all_articles_as_task = Field(TaskResponse, filter=ArticleFilterArgument())
    all_articles_task_result = relay.ConnectionField(ArticleConnection, task_id=String())

    def resolve_all_articles(root, info, **kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'article')
        return res

    def resolve_all_articles_as_task(root, info, **kwargs):
        task = resolve_all_task.apply_async(args=[kwargs, 'article'], queue='graphql_api')
        response = {'id': task.id, 'status': task.status, 'result': task.result}
        return response

    def resolve_all_articles_task_result(root, info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []

