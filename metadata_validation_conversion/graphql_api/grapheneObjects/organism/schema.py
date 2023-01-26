from graphene import ObjectType, String, Field, ID, relay, List, Int
from graphene.relay import Connection, Node
from ..common_field_objects import TaskResponse
from ...tasks import launch_celery_task
from ..helpers import fetch_index_records, fetch_with_join
from .field_objects import OrganismCustomFieldField, FileOrganizationField, OrganismPublishedArticlesField, \
    OrganismJoinField, TextUnitField, TextOntologyTermsField
from .arguments.filter import OrganismFilterArgument

from celery.result import AsyncResult


def fetch_single_organism(args):
    q = ''

    if args['id']:
        q = [{"terms": {"biosampleId": [args['id']]}}]
    elif args['alternate_id']:
        q = [{"terms": {"alternateId": [args['alternate_id']]}}]

    res = fetch_index_records('organism', filter=q)[0]
    res['id'] = res['biosampleId']
    return res


class OrganismNode(ObjectType):
    class Meta:
        interfaces = (Node,)

    biosampleId = String()
    id_number = Int()
    alternativeId = List(String)
    etag = String()
    name = String()
    description = String()
    releaseDate = String()
    updateDate = String()
    standardMet = String()
    versionLastStandardMet = String()
    project = String()
    secondaryProject = String()
    organization = List(of_type=FileOrganizationField)
    customField = List(of_type=OrganismCustomFieldField)
    material = Field(TextOntologyTermsField)
    availability = String()
    organism = Field(TextOntologyTermsField)
    sex = Field(TextOntologyTermsField)
    breed = Field(TextOntologyTermsField)
    birthDate = Field(TextUnitField)
    healthStatus = List(of_type=TextOntologyTermsField)
    birthLocation = String()
    birthLocationLongitude = Field(TextUnitField)
    birthLocationLatitude = Field(TextUnitField)
    birthWeight = Field(TextUnitField)
    placentalWeight = Field(TextUnitField)
    pregnancyLength = Field(TextUnitField)
    deliveryTiming = String()
    deliveryEase = String()
    childOf = String()
    pedigree = String()
    paperPublished = String()
    publishedArticles = Field(OrganismPublishedArticlesField)
    join = Field(OrganismJoinField)

    @classmethod
    def get_node(cls, info, id):
        args = {'id': id}
        return fetch_single_organism(args)


class OrganismConnection(Connection):
    class Meta:
        node = OrganismNode

    class Edge:
        pass


class OrganismSchema(ObjectType):
    organism = Field(OrganismNode, id=ID(required=True), alternate_id=ID(required=False))
    all_organisms = relay.ConnectionField(OrganismConnection, filter=OrganismFilterArgument())
    all_organisms_as_task = Field(TaskResponse, filter=OrganismFilterArgument())
    all_organisms_task_result = relay.ConnectionField(OrganismConnection, task_id=String())

    def resolve_organism(root, info, **args):
        return fetch_single_organism(args)

    def resolve_all_organisms(root, info, **kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'organism')
        return res

    def resolve_all_organisms_as_task(root, info, **kwargs):
        task = launch_celery_task.apply_async(args=[kwargs, 'organism'], queue='graphql_api')
        response = {'id': task.id, 'status': task.status, 'result': task.result}
        return response

    def resolve_all_organisms_task_result(root, info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []

