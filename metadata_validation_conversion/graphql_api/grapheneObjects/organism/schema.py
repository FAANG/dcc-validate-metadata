from graphene import ObjectType, String, Field, relay, List, Int
from graphene.relay import Connection, Node
from ..commonFieldObjects import TaskResponse
from ...tasks import resolve_all_task
from ..helpers import fetch_with_join
from .fieldObjects import Organism_Field, OrganismCustomFieldField, BirthDate_Field, BirthLocationLatitude_Field, \
    BirthLocationLongitude_Field, BirthWeight_Field, Breed_Field, HealthStatusField, Material_Field, \
    FileOrganizationField, PlacentalWeight_Field, PregnancyLength_Field, OrganismPublishedArticles_Field, Sex_Field, \
    OrganismJoin_Field
from .arguments.filter import OrganismFilterArgument

from celery.result import AsyncResult


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
    material = Field(Material_Field)
    availability = String()
    organism = Field(Organism_Field)
    sex = Field(Sex_Field)
    breed = Field(Breed_Field)
    birthDate = Field(BirthDate_Field)
    healthStatus = List(of_type=HealthStatusField)
    birthLocation = String()
    birthLocationLongitude = Field(BirthLocationLongitude_Field)
    birthLocationLatitude = Field(BirthLocationLatitude_Field)
    birthWeight = Field(BirthWeight_Field)
    placentalWeight = Field(PlacentalWeight_Field)
    pregnancyLength = Field(PregnancyLength_Field)
    deliveryTiming = String()
    deliveryEase = String()
    childOf = String()
    pedigree = String()
    paperPublished = String()
    publishedArticles = Field(OrganismPublishedArticles_Field)
    join = Field(OrganismJoin_Field)


class OrganismConnection(Connection):
    class Meta:
        node = OrganismNode

    class Edge:
        pass


class OrganismSchema(ObjectType):
    all_organisms = relay.ConnectionField(OrganismConnection, filter=OrganismFilterArgument())
    all_organisms_as_task = Field(TaskResponse, filter=OrganismFilterArgument())
    all_organisms_task_result = relay.ConnectionField(OrganismConnection, task_id=String())

    def resolve_all_organisms(root, info, **kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'organism')
        return res

    def resolve_all_organisms_as_task(root, info, **kwargs):
        task = resolve_all_task.apply_async(args=[kwargs, 'organism'], queue='graphql_api')
        response = {'id': task.id, 'status': task.status, 'result': task.result}
        return response

    def resolve_all_organisms_task_result(root, info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []

