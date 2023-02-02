from graphene import ObjectType, String, Field,ID, relay, List, Int
from graphene.relay import Connection,Node
from graphql_api.tasks import launch_celery_task
from celery.result import AsyncResult
from ..helpers import fetch_index_records, fetch_with_join
from .field_objects import CellCultureField,SpecimenOrganismField,CellLineField,CellSpecimenField,\
    SpecimenOrganizationField,PoolOfSpecimensField,SpecimenPublishedArticlesField,SpecimenCustomFieldField,\
    SpecimenFromOrganismField,SpecimenJoinField
from .arguments.filter import SpecimenFilterArgument
from ..common_field_objects import OntologyField, TaskResponse


def fetch_single_specimen(args):
    q = ''

    if args['id']:
        q = [{"terms": {"biosampleId": [args['id']]}}]
    elif args['alternate_id']:
        q = [{"terms": {"alternateId": [args['alternate_id']]}}]

    res = fetch_index_records('specimen', filter=q)[0]
    res['id'] = res['biosampleId']
    return res


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
    organism = Field(SpecimenOrganismField)
    specimenFromOrganism = Field(SpecimenFromOrganismField)
    poolOfSpecimens = Field(PoolOfSpecimensField)
    cellSpecimen = Field(CellSpecimenField)
    cellCulture = Field(CellCultureField)
    cellLine = Field(CellLineField)
    paperPublished = String()
    publishedArticles = List(of_type=SpecimenPublishedArticlesField)
    trackhubUrl = String()
    join = Field(SpecimenJoinField)

    @classmethod
    def get_node(cls, info, id):
        args = {'id':id}
        return fetch_single_specimen(args)

class SpecimenConnection(Connection):
    class Meta:
        node = SpecimenNode
    
    class Edge:
        pass


class SpecimenSchema(ObjectType):
    specimen = Field(SpecimenNode,id = ID(required=True), alternate_id = ID(required = False))
    all_specimens = relay.ConnectionField(SpecimenConnection, filter=SpecimenFilterArgument())
    all_specimens_as_task = Field(TaskResponse, filter=SpecimenFilterArgument())
    all_specimens_task_result = relay.ConnectionField(SpecimenConnection,task_id=String())

    def resolve_specimen(root,info,**args):
        return fetch_single_specimen(args)

    def resolve_all_specimens(root, info,**kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'specimen')
        return res

    def resolve_all_specimens_as_task(root, info,**kwargs):
        task = launch_celery_task.apply_async(args=[kwargs, 'specimen'], queue='graphql_api')
        response = {'id':task.id,'status':task.status,'result':task.result}
        return response

    def resolve_all_specimens_task_result(root,info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []
