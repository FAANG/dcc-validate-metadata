from decouple import config

BASE_URL = "https://raw.githubusercontent.com/FAANG/dcc-metadata/" \
           "switch_to_json-schema/json_schema/"
SAMPLE_CORE_URL = f"{BASE_URL}core/samples/" \
                  f"faang_samples_core.metadata_rules.json"
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
ELIXIR_VALIDATOR_URL = config('ELIXIR_VALIDATOR_URL')
WS_URL = "ws://127.0.0.1:8000/ws/submission/test_task/"

ALLOWED_SHEET_NAMES = {
    'organism': ORGANISM_URL,
    'specimen from organism': SPECIMEN_FROM_ORGANISM_URL,
    'pool of specimens': POOL_OF_SPECIMENS_URL,
    'cell specimen': CELL_SPECIMEN_URL,
    'cell culture': CELL_CULTURE_URL,
    'cell line': CELL_LINE_URL
}

ALLOWED_RECORD_TYPES = {
    'organism': ORGANISM_URL,
    'specimen_from_organism': SPECIMEN_FROM_ORGANISM_URL,
    'pool_of_specimens': POOL_OF_SPECIMENS_URL,
    'cell_specimen': CELL_SPECIMEN_URL,
    'cell_culture': CELL_CULTURE_URL,
    'cell_line': CELL_LINE_URL
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

SKIP_PROPERTIES = ['describedBy', 'schema_version', 'samples_core']

SPECIAL_PROPERTIES = ['unit', 'term_source_id']

JSON_TYPES = {
    'core': 'samples_core',
    'type': None,
    'custom': 'custom'
}


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
