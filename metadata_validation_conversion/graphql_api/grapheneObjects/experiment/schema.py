from graphene import ObjectType, String, Field, relay
from graphene.relay import Connection, Node
from graphql_api.tasks import resolve_all_task
from celery.result import AsyncResult
from ..helpers import fetch_with_join
from .fieldObjects import ATACseqField, BsSeqField, CAGEseqField, ChIPSeqDnaBindingField, \
    ChIPseqInputDNAField, DNaseSeqField, ExperimentCustomFieldField, ExperimentJoinField, HiCField, \
    RNAseqField, WGSField
from .arguments.filter import ExperimentFilterArgument
from ..commonFieldObjects import ProtocolField, UnitField, TaskResponse


class ExperimentNode(ObjectType):
    class Meta:
        interfaces = (Node,)

    accession = String()
    project = String()
    secondaryProject = String()
    assayType = String()
    experimentTarget = String()
    standardMet = String()
    versionLastStandardMet = String()
    libraryName = String()
    sampleStorage = String()
    sampleStorageProcessing = String()
    samplingToPreparationInterval = Field(UnitField)
    experimentalProtocol = Field(ProtocolField)
    extractionProtocol = Field(ProtocolField)
    libraryPreparationLocation = String()
    libraryPreparationLocationLatitude = Field(UnitField)
    libraryPreparationLocationLongitude = Field(UnitField)
    libraryPreparationDate = Field(UnitField)
    sequencingLocation = String()
    sequencingLocationLongitude = Field(UnitField)
    sequencingLocationLatitude = Field(UnitField)
    sequencingDate = Field(UnitField)
    customField = Field(ExperimentCustomFieldField)
    ATACSeq = Field(ATACseqField)
    BsSeq = Field(BsSeqField)
    ChIPSeqDnaBinding = Field(ChIPSeqDnaBindingField)
    HiC = Field(HiCField)
    RNASeq = Field(RNAseqField)
    WGS = Field(WGSField)
    CAGESeq = Field(CAGEseqField)

    ChIP_seq_input_DNA = Field(ChIPseqInputDNAField)
    DNase_seq = Field(DNaseSeqField)

    join = Field(ExperimentJoinField)


class ExperimentConnection(Connection):
    class Meta:
        node = ExperimentNode

    class Edge:
        pass


class ExperimentSchema(ObjectType):
    all_experiments = relay.ConnectionField(ExperimentConnection, filter=ExperimentFilterArgument())
    all_experiments_as_task = Field(TaskResponse, filter=ExperimentFilterArgument())
    all_experiments_task_result = relay.ConnectionField(ExperimentConnection, task_id=String())

    def resolve_all_experiments(root, info, **kwargs):
        filter_query = kwargs['filter'] if 'filter' in kwargs else {}
        res = fetch_with_join(filter_query, 'experiment')
        return res

    def resolve_all_experiments_as_task(root, info, **kwargs):
        task = resolve_all_task.apply_async(args=[kwargs, 'experiment'], queue='graphql_api')
        response = {'id': task.id, 'status': task.status, 'result': task.result}
        return response

    def resolve_all_experiments_task_result(root, info, **kwargs):
        task_id = kwargs['task_id']
        res = AsyncResult(task_id).result
        return res if res else []