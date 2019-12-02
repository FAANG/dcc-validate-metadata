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


ALLOWED_SHEET_NAMES = {
    'organism': ORGANISM_URL,
    'specimen from organism': SPECIMEN_FROM_ORGANISM_URL,
    'pool of specimens': POOL_OF_SPECIMENS_URL,
    'cell specimen': CELL_SPECIMEN_URL,
    'cell culture': CELL_CULTURE_URL,
    'cell line': CELL_LINE_URL,
    'wgs': WGS_URL,
    'rna-seq': RNA_SEQ_URL,
    'hi-c': HI_C_URL,
    'dnase-seq': DNASE_SEQ_URL,
    'chip-seq input dna': CHIP_SEQ_URL,
    'chip-seq dna-binding proteins': CHIP_SEQ_URL,
    'bs-seq': BS_SEQ_URL,
    'atac-seq': ATAC_SEQ_URL,
    'faang': FAANG_ANALYSES_URL,
    'ena': ENA_ANALYSES_URL,
    'eva': EVA_ANALYSES_URL
}

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
    'chip-seq_input_dna': CHIP_SEQ_URL,
    'chip-seq_dna-binding_proteins': CHIP_SEQ_URL,
    'bs-seq': BS_SEQ_URL,
    'atac-seq': ATAC_SEQ_URL
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
