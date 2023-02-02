from graphene import ObjectType, String, Field, ID, relay, List
from graphene.relay import Connection, Node
from graphql_api.tasks import launch_celery_task
from celery.result import AsyncResult
from ..helpers import fetch_index_records, fetch_with_join
from .field_objects import RelatedDatasets_Field, ArticleJoin_Field
from .arguments.filter import ArticleFilterArgument
from ..common_field_objects import TaskResponse


def fetch_single_article(args):
    q = [{
        "bool": {
            "should": [
                {"term": {"pmcId": args['id']}},
                {"term": {"pubmedId": args['id']}}
            ]
        }
    }]
    res = fetch_index_records('article', filter=q)[0]
    res['id'] = res['pmcId'] if res['pmcId'] else res['pubmedId']
    return res


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

    @classmethod
    def get_node(cls, info, id):
        return fetch_single_article({'id': id})


class ArticleConnection(Connection):
    class Meta:
        node = ArticleNode

    class Edge:
        pass


class ArticleSchema(ObjectType):
    article = Field(ArticleNode, id=ID(required=True), alternate_id=ID(required=False))
    all_articles = relay.ConnectionField(ArticleConnection, filter=ArticleFilterArgument())
    all_articles_as_task = Field(TaskResponse, filter=ArticleFilterArgument())
    all_articles_task_result = relay.ConnectionField(ArticleConnection, task_id=String())

    def resolve_article(root, info, **args):
        return fetch_single_article(args)

    def resolve_all_articles(root, info, **kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'article')
        return res

    def resolve_all_articles_as_task(root, info, **kwargs):
        task = launch_celery_task.apply_async(args=[kwargs, 'article'], queue='graphql_api')
        response = {'id': task.id, 'status': task.status, 'result': task.result}
        return response

    def resolve_all_articles_task_result(root, info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []

