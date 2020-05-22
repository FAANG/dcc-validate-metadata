from decouple import config

BASE_URL = "https://raw.githubusercontent.com/FAANG/dcc-metadata/" \
           "switch_to_json-schema/json_schema/"
SAMPLE_CORE_URL = f"{BASE_URL}core/samples/" \
                  f"faang_samples_core.metadata_rules.json"
EXPERIMENT_CORE_URL = f"{BASE_URL}/core/experiments/" \
                      f"faang_experiments_core.metadata_rules.json"
ORGANISM_URL = f"{BASE_URL}type/samples/" \
               f"faang_samples_organism.metadata_rules.json"
SPECIMEN_FROM_ORGANISM_URL = f"{BASE_URL}type/samples/" \
                             f"faang_samples_specimen.metadata_rules.json"
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
HI_C_URL = f"{BASE_URL}/type/experiments/" \
           f"faang_experiments_hi-c.metadata_rules.json"
DNASE_SEQ_URL = f"{BASE_URL}/type/experiments/" \
                f"faang_experiments_dnase-seq.metadata_rules.json"
CAGE_SEQ_URL = f"{BASE_URL}/type/experiments/" \
                f"faang_experiments_cage-seq.metadata_rules.json"
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
ATAC_SEQ_URL = f"{BASE_URL}/type/experiments/" \
               f"faang_experiments_atac-seq.metadata_rules.json"
FAANG_ANALYSES_URL = f"{BASE_URL}/type/analyses/" \
                     f"faang_analyses_faang.metadata_rules.json"
ENA_ANALYSES_URL = f"{BASE_URL}/type/analyses/" \
                   f"faang_analyses_ena.metadata_rules.json"
EVA_ANALYSES_URL = f"{BASE_URL}/module/analyses/" \
                   f"faang_analyses_eva.metadata_rules.json"
ELIXIR_VALIDATOR_URL = config('ELIXIR_VALIDATOR_URL')
WS_URL = "ws://127.0.0.1:8000/ws/submission/test_task/"

SAMPLE = 'samples'
EXPERIMENT = 'experiments'
ANALYSIS = 'analyses'

MINIMUM_TEMPLATE_VERSION_REQUIREMENT = 1.1

# keys are sheet sheet_name used in the template
ALLOWED_SAMPLES_TYPES = {
    'organism': ORGANISM_URL,
    'specimen_from_organism': SPECIMEN_FROM_ORGANISM_URL,
    'pool_of_specimens': POOL_OF_SPECIMENS_URL,
    'cell_specimen': CELL_SPECIMEN_URL,
    'cell_culture': CELL_CULTURE_URL,
    'cell_line': CELL_LINE_URL
}

ALLOWED_EXPERIMENTS_TYPES = {
    'wgs': WGS_URL,
    'rna-seq': RNA_SEQ_URL,
    'hi-c': HI_C_URL,
    'dnase-seq': DNASE_SEQ_URL,
    'cage-seq': CAGE_SEQ_URL,
    'chip-seq_input_dna': CHIP_SEQ_URL,
    'chip-seq_dna-binding_proteins': CHIP_SEQ_URL,
    'bs-seq': BS_SEQ_URL,
    'atac-seq': ATAC_SEQ_URL
}

ALLOWED_ANALYSES_TYPES = {
    'faang': FAANG_ANALYSES_URL,
    'ena': ENA_ANALYSES_URL,
    'eva': EVA_ANALYSES_URL
}

ALLOWED_SHEET_NAMES = {
    SAMPLE: ALLOWED_SAMPLES_TYPES,
    EXPERIMENT: ALLOWED_EXPERIMENTS_TYPES,
    ANALYSIS: ALLOWED_ANALYSES_TYPES
}


# column index starts from 0
ID_COLUMNS_WITH_INDICES = {
    SAMPLE: {'sample_name': 0},
    EXPERIMENT: {'sample_descriptor': 0, 'experiment_alias': 1},
    ANALYSIS: {'alias': 0}
}

ALLOWED_RELATIONSHIPS = {
    'organism': ['organism'],
    'specimen_from_organism': ['organism'],
    'pool_of_specimens': ['specimen_from_organism'],
    'cell_specimen': ['specimen_from_organism'],
    'cell_culture': ['specimen_from_organism', 'cell_specimen'],
    'cell_line': ['organism', 'specimen_from_organism', 'pool_of_specimens',
                  'cell_specimen', 'cell_culture', 'cell_line']
}

# map_field_for_locations are conserved keywords, map_field_for_locations are with JSON pointer for the purpose of reusage, recursion etc
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

# Mandatory fields refer to https://raw.githubusercontent.com/enasequence/schema/master/src/main/resources/
# uk/ac/ebi/ena/sra/schema/SRA.experiment.xsd
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
        # required by ExperimentType
        'study_ref',
        # required by LibraryType
        'design_description',
        # required by FAANG community (workshop 2020)
        'library_name',
        # required by LibraryDescriptorType
        'library_strategy',
        'library_source',
        'library_selection',
        'library_layout',
        # required by com:PlatformType
        'platform',
        'instrument_model'
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
    # refers to https://raw.githubusercontent.com/enasequence/schema/master/src/main/resources/
    # uk/ac/ebi/ena/sra/schema/SRA.run.xsd
    'mandatory': [
        'alias',
        # required by FAANG
        'run_center',
        'run_date',
        # required by Run
        'experiment_ref',
        # required by FILE element
        'filename',
        'filetype',
        'checksum_method',
        'checksum',
    ]
}

EXPERIMENT_ALLOWED_SPECIAL_SHEET_NAMES = {
    'study': STUDY_FIELDS,
    'experiment_ena': EXPERIMENT_ENA_FIELDS,
    'submission': SUBMISSION_FIELDS,
    'run': RUN_FIELDS
}

SPECIAL_SHEETS = {
    EXPERIMENT: EXPERIMENT_ALLOWED_SPECIAL_SHEET_NAMES
}

CHIP_SEQ_MODULE_RULES = {
    'chip-seq input dna': CHIP_SEQ_INPUT_DNA_URL,
    'chip-seq dna-binding proteins': CHIP_SEQ_DNA_BINDING_PROTEINS_URL
}

FIELD_NAMES = {
    SAMPLE: {
        'core_name': 'samples_core',
        'record_column_name': 'Sample Name',
        'record_name': 'sample_name'
    },
    EXPERIMENT: {
        'core_name': 'experiments_core',
        'record_column_name': 'Sample Descriptor',
        'record_name': 'sample_descriptor'
    },
    ANALYSIS: {
        'record_column_name': 'Alias',
        'record_name': 'alias'
    }
}
