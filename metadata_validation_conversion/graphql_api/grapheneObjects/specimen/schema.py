from graphene import ObjectType, String, Field, relay, List, Int
from graphene.relay import Connection,Node
from graphql_api.tasks import resolve_all_task
from celery.result import AsyncResult
from ..helpers import fetch_with_join
from .fieldObjects import CellCultureField,SpecimenOrganismField,CellLineField,CellSpecimenField,\
    SpecimenOrganizationField,PoolOfSpecimensField,SpecimenPublishedArticlesField,SpecimenCustomFieldField,\
    SpecimenFromOrganismField,SpecimenJoinField
from .arguments.filter import SpecimenFilterArgument
from ..commonFieldObjects import OntologyField, TaskResponse


class SpecimenNode(ObjectType):
    class Meta:
        interfaces = (Node, )
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
    organization = List(of_type=SpecimenOrganizationField)
    customField = List(of_type=SpecimenCustomFieldField)
    material = Field(OntologyField)
    derivedFrom = String()
    allDeriveFromSpecimens = String()
    availability = String()
    cellType = Field(OntologyField)
    specimen = Field(SpecimenOrganismField)
    specimenFromOrganism = Field(SpecimenFromOrganismField)
    poolOfSpecimens = Field(PoolOfSpecimensField)
    cellSpecimen = Field(CellSpecimenField)
    cellCulture = Field(CellCultureField)
    cellLine = Field(CellLineField)
    paperPublished = String()
    publishedArticles = List(of_type=SpecimenPublishedArticlesField)
    trackhubUrl = String()
    join = Field(SpecimenJoinField)


class SpecimenConnection(Connection):
    class Meta:
        node = SpecimenNode
    
    class Edge:
        pass


class SpecimenSchema(ObjectType):
    all_specimens = relay.ConnectionField(SpecimenConnection, filter=SpecimenFilterArgument())
    all_specimens_as_task = Field(TaskResponse, filter=SpecimenFilterArgument())
    all_specimens_task_result = relay.ConnectionField(SpecimenConnection,task_id=String())

    def resolve_all_specimens(root, info,**kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'specimen')
        return res

    def resolve_all_specimens_as_task(root, info,**kwargs):
        task = resolve_all_task.apply_async(args=[kwargs,'specimen'],queue='graphql_api')
        response = {'id':task.id,'status':task.status,'result':task.result}
        return response

    def resolve_all_specimens_task_result(root,info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []
