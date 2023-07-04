from decouple import config

BASE_URL = "https://raw.githubusercontent.com/FAANG/dcc-metadata/master/" \
           "json_schema/"
SAMPLE_CORE_URL = f"{BASE_URL}core/samples/" \
                  f"faang_samples_core.metadata_rules.json"
EXPERIMENT_CORE_URL = f"{BASE_URL}/core/experiments/" \
                      f"faang_experiments_core.metadata_rules.json"
ORGANISM_URL = f"{BASE_URL}type/samples/" \
               f"faang_samples_organism.metadata_rules.json"
ORGANOID_URL = f"{BASE_URL}type/samples/" \
               f"faang_samples_organoid.metadata_rules.json"
SPECIMEN_FROM_ORGANISM_URL = f"{BASE_URL}type/samples/" \
                             f"faang_samples_specimen.metadata_rules.json"
TELEOSTEI_EMBRYO_URL = f"{BASE_URL}module/samples/" \
                       f"faang_samples_specimen_teleost_embryo" \
                       f".metadata_rules.json"
TELEOSTEI_POST_HATCHING_URL = f"{BASE_URL}module/samples/" \
                              f"faang_samples_specimen_teleost_post-hatching" \
                              f".metadata_rules.json"
SINGLE_CELL_SPECIMEN_URL = f"{BASE_URL}type/samples/" \
                           f"faang_samples_single_cell_specimen" \
                           f".metadata_rules.json"
POOL_OF_SPECIMENS_URL = f"{BASE_URL}type/samples/" \
                        f"faang_samples_pool_of_specimens.metadata_rules.json"
CELL_SPECIMEN_URL = f"{BASE_URL}type/samples/" \
                    f"faang_samples_purified_cells.metadata_rules.json"
CELL_CULTURE_URL = f"{BASE_URL}type/samples/" \
                   f"faang_samples_cell_culture.metadata_rules.json"
CELL_LINE_URL = f"{BASE_URL}type/samples/" \
                f"faang_samples_cell_line.metadata_rules.json"
WGS_URL = f"{BASE_URL}/type/experiments/" \
          f"faang_experiments_wgs.metadata_rules.json"
RNA_SEQ_URL = f"{BASE_URL}/type/experiments/" \
              f"faang_experiments_rna-seq.metadata_rules.json"
SCRNA_SEQ_URL = f"{BASE_URL}/type/experiments/" \
              f"faang_experiments_scrna-seq.metadata_rules.json"
HI_C_URL = f"{BASE_URL}/type/experiments/" \
           f"faang_experiments_hi-c.metadata_rules.json"
DNASE_SEQ_URL = f"{BASE_URL}/type/experiments/" \
                f"faang_experiments_dnase-seq.metadata_rules.json"
CHIP_SEQ_URL = f"{BASE_URL}/type/experiments/" \
               f"faang_experiments_chip-seq.metadata_rules.json"
CHIP_SEQ_INPUT_DNA_URL = f"{BASE_URL}/module/experiments/" \
                         f"faang_experiments_chip-seq_input_dna.metadata_" \
                         f"rules.json"
CHIP_SEQ_DNA_BINDING_PROTEINS_URL = f"{BASE_URL}/module/experiments/" \
                                    f"faang_experiments_chip-seq_dna-binding_" \
                                    f"proteins.metadata_rules.json"
BS_SEQ_URL = f"{BASE_URL}/type/experiments/" \
             f"faang_experiments_bs-seq.metadata_rules.json"
EM_SEQ_URL = f"{BASE_URL}/type/experiments/" \
             f"faang_experiments_em-seq.metadata_rules.json"
ATAC_SEQ_URL = f"{BASE_URL}/type/experiments/" \
               f"faang_experiments_atac-seq.metadata_rules.json"
CAGE_SEQ_URL = f"{BASE_URL}/type/experiments/" \
               f"faang_experiments_cage-seq.metadata_rules.json"
FAANG_ANALYSES_URL = f"{BASE_URL}/type/analyses/" \
                     f"faang_analyses_faang.metadata_rules.json"
ENA_ANALYSES_URL = f"{BASE_URL}/type/analyses/" \
                   f"faang_analyses_ena.metadata_rules.json"
EVA_ANALYSES_URL = f"{BASE_URL}/module/analyses/" \
                   f"faang_analyses_eva.metadata_rules.json"
ELIXIR_VALIDATOR_URL = config('ELIXIR_VALIDATOR_URL')
WS_URL = "ws://127.0.0.1:8000/ws/submission/test_task/"

ALLOWED_TEMPLATES = ['samples', 'experiments', 'analyses']


ALLOWED_SHEET_NAMES = {
    'organism': ORGANISM_URL,
    'organoid': ORGANOID_URL,
    'specimen from organism': SPECIMEN_FROM_ORGANISM_URL,
    "teleostei embryo": SPECIMEN_FROM_ORGANISM_URL,
    "teleostei post-hatching": SPECIMEN_FROM_ORGANISM_URL,
    'pool of specimens': POOL_OF_SPECIMENS_URL,
    'cell specimen': CELL_SPECIMEN_URL,
    'single cell specimen': SINGLE_CELL_SPECIMEN_URL,
    'cell culture': CELL_CULTURE_URL,
    'cell line': CELL_LINE_URL,
    'wgs': WGS_URL,
    'rna-seq': RNA_SEQ_URL,
    'scrna-seq': SCRNA_SEQ_URL,
    'hi-c': HI_C_URL,
    'dnase-seq': DNASE_SEQ_URL,
    'chip-seq input dna': CHIP_SEQ_URL,
    'chip-seq dna-binding proteins': CHIP_SEQ_URL,
    'bs-seq': BS_SEQ_URL,
    'em-seq': EM_SEQ_URL,
    'atac-seq': ATAC_SEQ_URL,
    'cage-seq': CAGE_SEQ_URL,
    'faang': FAANG_ANALYSES_URL,
    'ena': ENA_ANALYSES_URL,
    'eva': EVA_ANALYSES_URL
}

ALLOWED_SAMPLES_TYPES = {
    'organism': ORGANISM_URL,
    'specimen_from_organism': SPECIMEN_FROM_ORGANISM_URL,
    'teleostei_embryo': SPECIMEN_FROM_ORGANISM_URL,
    'teleostei_post-hatching': SPECIMEN_FROM_ORGANISM_URL,
    'pool_of_specimens': POOL_OF_SPECIMENS_URL,
    'cell_specimen': CELL_SPECIMEN_URL,
    'single_cell_specimen': SINGLE_CELL_SPECIMEN_URL,
    'cell_culture': CELL_CULTURE_URL,
    'cell_line': CELL_LINE_URL
}

ALLOWED_EXPERIMENTS_TYPES = {
    'wgs': WGS_URL,
    'rna-seq': RNA_SEQ_URL,
    'scrna-seq': SCRNA_SEQ_URL,
    'hi-c': HI_C_URL,
    'dnase-seq': DNASE_SEQ_URL,
    'chip-seq_input_dna': CHIP_SEQ_URL,
    'chip-seq_dna-binding_proteins': CHIP_SEQ_URL,
    'bs-seq': BS_SEQ_URL,
    'em-seq': EM_SEQ_URL,
    'atac-seq': ATAC_SEQ_URL,
    'cage-seq': CAGE_SEQ_URL
}

ALLOWED_ANALYSES_TYPES = {
    'faang': FAANG_ANALYSES_URL,
    'ena': ENA_ANALYSES_URL,
    'eva': EVA_ANALYSES_URL
}

ALLOWED_RELATIONSHIPS = {
    'organism': ['organism'],
    'specimen_from_organism': ['organism'],
    'teleostei_embryo': ['organism'],
    'teleostei_post-hatching': ['organism'],
    'pool_of_specimens': ['specimen_from_organism', 'teleostei_embryo',
                          'teleostei_post-hatching', 'cell_specimen',
                          'single_cell_specimen'],
    'cell_specimen': ['specimen_from_organism'],
    'single_cell_specimen': ['specimen_from_organism'],
    'cell_culture': ['specimen_from_organism', 'cell_specimen'],
    'cell_line': ['organism', 'specimen_from_organism', 'pool_of_specimens',
                  'cell_specimen', 'cell_culture', 'cell_line']
}

SKIP_PROPERTIES = [
    'describedBy',
    'schema_version',
    'samples_core',
    'experiments_core',
    'dna-binding_proteins',
    'input_dna',
    'eva'
]

SPECIAL_PROPERTIES = ['unit', 'term_source_id']

JSON_TYPES = {
    'type': None,
    'custom': 'custom'
}

SAMPLES_SPECIFIC_JSON_TYPES = {
    'core': 'samples_core'
}

SPECIMEN_TELEOST_EMBRYO_JSON_TYPES = {
    'module': 'teleostei_embryo'
}

SPECIMEN_TELEOST_POST_HATCHING_JSON_TYPES = {
    'module': 'teleostei_post-hatching'
}

EXPERIMENTS_SPECIFIC_JSON_TYPES = {
    'core': 'experiments_core'
}

CHIP_SEQ_INPUT_DNA_JSON_TYPES = {
    'module': 'input_dna'
}

CHIP_SEQ_DNA_BINDING_PROTEINS_JSON_TYPES = {
    'module': 'dna-binding_proteins'
}

MODULE_SHEET_NAMES = [
    'chip-seq_input_dna',
    'chip-seq_dna-binding_proteins'
]


MISSING_VALUES = {
    'mandatory': {
        'errors': ["not applicable", "not collected", "not provided"],
        "warnings": ["restricted access"]
    },
    'recommended': {
        'errors': [],
        'warnings': ["not collected", "not provided"]
    },
    'optional': {
        'errors': ["not applicable", "not collected", "not provided",
                   "restricted access"],
        'warnings': []
    }
}

SPECIES_BREED_LINKS = {
    "NCBITaxon:89462": "LBO:0001042",  # buffalo (Bubalus bubalis)
    "NCBITaxon:9913": "LBO:0000001",  # cattle (Bos taurus)
    "NCBITaxon:9031": "LBO:0000002",  # chicken
    "NCBITaxon:9925": "LBO:0000954",  # goat
    "NCBITaxon:9796": "LBO:0000713",  # horse
    "NCBITaxon:9823": "LBO:0000003",  # pig
    "NCBITaxon:9940": "LBO:0000004"  # sheep
}

STUDY_FIELDS = {
    'all': ['study_alias', 'study_title', 'study_type', 'study_abstract'],
    'mandatory': ['study_alias', 'study_title', 'study_type']
}

EXPERIMENT_ENA_FIELDS = {
    'all': [
        'sample_descriptor',
        'experiment_alias',
        'title',
        'study_ref',
        'design_description',
        'library_name',
        'library_strategy',
        'library_source',
        'library_selection',
        'library_layout',
        'nominal_length',
        'nominal_sdev',
        'library_construction_protocol',
        'platform',
        'instrument_model'
    ],
    'mandatory': [
        'sample_descriptor',
        'experiment_alias',
        'study_ref',
        'design_description',
        'library_strategy',
        'library_source',
        'library_selection',
        'library_layout',
        'platform'
    ]
}

SUBMISSION_FIELDS = {
    'all': ['alias'],
    'mandatory': ['alias']
}

RUN_FIELDS = {
    'all': [
        'alias',
        'run_center',
        'run_date',
        'experiment_ref',
        'filename',
        'filetype',
        'checksum_method',
        'checksum',
        'filename_pair',
        'filetype_pair',
        'checksum_method_pair',
        'checksum_pair'
    ],
    'mandatory': [
        'alias',
        'run_center',
        'experiment_ref',
        'filename',
        'filetype',
        'checksum_method',
        'checksum',
    ]
}

PERSON_FIELDS = {
    'all': [
        'person_last_name',
        'person_initials',
        'person_first_name',
        'person_email',
        'person_role'
    ],
    'mandatory': [
        'person_last_name',
        'person_first_name',
        'person_email',
        'person_role'
    ]
}

ORGANIZATION_FIELDS = {
    'all': [
        'organization_name',
        'organization_address',
        'organization_uri',
        'organization_role'
    ],
    'mandatory': [
        'organization_name',
        'organization_address',
        'organization_uri',
        'organization_role'
    ]
}

SAMPLES_SUBMISSION_FIELDS = {
    'all': [
        'submission_title',
        'submission_description'
    ],
    'mandatory': [
        'submission_title',
        'submission_description'
    ]
}

EXPERIMENT_ALLOWED_SPECIAL_SHEET_NAMES = {
    'study': STUDY_FIELDS,
    'experiment ena': EXPERIMENT_ENA_FIELDS,
    'submission': SUBMISSION_FIELDS,
    'run': RUN_FIELDS
}

SAMPLES_ALLOWED_SPECIAL_SHEET_NAMES = {
    'person': PERSON_FIELDS,
    'organization': ORGANIZATION_FIELDS,
    'submission': SAMPLES_SUBMISSION_FIELDS
}

MODULE_RULES = {
    'teleostei embryo': TELEOSTEI_EMBRYO_URL,
    'teleostei_embryo': TELEOSTEI_EMBRYO_URL,
    'teleostei post-hatching': TELEOSTEI_POST_HATCHING_URL,
    'teleostei_post-hatching': TELEOSTEI_POST_HATCHING_URL,
    'chip-seq input dna': CHIP_SEQ_INPUT_DNA_URL,
    'chip-seq_input_dna': CHIP_SEQ_INPUT_DNA_URL,
    'chip-seq dna-binding proteins': CHIP_SEQ_DNA_BINDING_PROTEINS_URL,
    'chip-seq_dna-binding_proteins': CHIP_SEQ_DNA_BINDING_PROTEINS_URL
}

FIELD_NAMES = {
    'samples': {
        'core_name': 'samples_core',
        'record_column_name': 'Sample Name',
        'record_name': 'sample_name'
    },
    'experiments': {
        'core_name': 'experiments_core',
        'record_column_name': 'Sample Descriptor',
        'record_name': 'sample_descriptor'
    },
    'analyses': {
        'record_column_name': 'Alias',
        'record_name': 'alias'
    }
}

ADDITIONAL_INFO_MAPPING = {
    'person_last_name': 'LastName',
    'person_initials': 'MidInitials',
    'person_first_name': 'FirstName',
    'person_email': 'E-mail',
    'person_role': 'Role',
    'organization_name': 'Name',
    'organization_address': 'Address',
    'organization_uri': 'URL',
    'organization_role': 'Role'
}

AAP_TEST_SERVER = 'https://explore.api.aai.ebi.ac.uk'
SUBMISSION_TEST_SERVER = 'https://wwwdev.ebi.ac.uk'
AAP_PROD_SERVER = 'https://api.aai.ebi.ac.uk'
SUBMISSION_PROD_SERVER = 'https://www.ebi.ac.uk'

ENA_TEST_SERVER = 'https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit/'
ENA_PROD_SERVER = 'https://www.ebi.ac.uk/ena/submit/drop-box/submit/'

BE_SVC = 'http://backend-svc:8000'
ZOOMA_SERVICE = 'http://www.ebi.ac.uk/spot/zooma/v2/api/services'

PROJECTS = [
    "AQUA-FAANG",
    "BovReg",
    "GENE-SWitCH",
    "Bovine-FAANG",
    "EFFICACE",
    "GEroNIMO",
    "RUMIGEN",
    "Equine-FAANG"
]

ORGANIZATIONS = {
    "ABDN": "University of Aberdeen (Aberdeen, UK)",
    "AGR": "AgResearch (New Zealand)",
    "AGS": "Agroscope (Switzerland)",
    "DEDJTR": "Department of Economic Development, Jobs, Transport and "
              "Resources (Bundoora, Australia)",
    "DIAGENODE": "Diagenode (Liège, Belgium)",
    "EHU": "University of the Basque Country (Spain)",
    "ESTEAM": "ESTeam Paris SUD (France)",
    "FBN": "Leibniz Institute for Farm Animal Biology (Dummerstorf, Germany)",
    "HCMR": "Hellenic Centre for Marine Research (Greece)",
    "INRA": "French National Institute for Agricultural Research (France)",
    "INRAE": "National Research Institute for Agriculture, Food and "
             "Environment (France）",
    "INSERM": "French National Institute of Health and Medical Research (France)",
    "INSERM-INRAE": "INSERM-INRAE",
    "Institut Agro": "L’institut Agro (Rennes, France)",
    "IRTA": "Institute of Agrifood Research and Technology (Spain)",
    "ISU": "Iowa State University (USA)",
    "KU": "Konkuk University (Seoul, Korea)",
    "NUID": "University College Dublin (Dublin, Ireland)",
    "NMBU": "Norwegian University of Life Sciences (Norway)",
    "QAAFI-UQ": "University of Queensland (Australia)",
    "ROSLIN": "Roslin Institute (Edinburgh, UK)",
    "TAMU": "Texas A&M University (USA)",
    "UAL": "University of Alberta (Canada)",
    "UCD": "University of California, Davis (USA)",
    "UD": "University of Delaware (USA)",
    "UDL": "University of Lleida (Catalonia, Spain)",
    "UIC": "University of Illinois at Chicago (USA)",
    "UIDAHO": "University of Idaho (USA)",
    "UIUC": "University of Illinois at Urbana–Champaign (USA)",
    "ULE": "University of León (León, Spain)",
    "UNIPD": "University of Padua (Italy)",
    "UNL": "University of Nebraska-Lincoln (USA)",
    "UOB": "University of Birmingham (UK)",
    "USC": "University of Santiago de Compostela (Spain)",
    "USDA": "The United States Department of Agriculture (USA)",
    "USMARC": "United States Meat Animal Research Center (USA)",
    "USU": "Utah State University (USA)",
    "WSU": "Washington State University(USA)",
    "WU": "Wageningen University (Netherlands)",
    "ZIGR": "Polish Academy of Sciences Institute of Ichthyobiology and Aquaculture in Golysz (Poland)"
}
