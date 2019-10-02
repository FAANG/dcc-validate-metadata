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

ALLOWED_SHEET_NAMES = {
    'organism': ORGANISM_URL,
    'specimen from organism': SPECIMEN_FROM_ORGANISM_URL,
    'pool of specimens': POOL_OF_SPECIMENS_URL,
    'cell specimen': CELL_SPECIMEN_URL,
    'cell culture': CELL_CULTURE_URL,
    'cell line': CELL_LINE_URL
}

ALLOWED_RECORD_TYPES = ['organism', 'specimen_from_organism',
                        'pool_of_specimens', 'cell_specimen', 'cell_culture',
                        'cell_line']

SKIP_PROPERTIES = ['describedBy', 'schema_version', 'samples_core']

SPECIAL_PROPERTIES = ['sample_name', 'unit', 'term_source_id']

JSON_TYPES = {
    'core': 'samples_core',
    'type': None,
    'custom': 'custom'
}
