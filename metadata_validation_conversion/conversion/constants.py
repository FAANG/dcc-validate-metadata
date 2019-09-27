BASE_URL = "https://raw.githubusercontent.com/FAANG/dcc-metadata/" \
           "switch_to_json-schema/json_schema/"
ORGANISM_URL = f"{BASE_URL}type/samples/" \
               f"faang_samples_organism.metadata_rules.json"

SKIP_PROPERTIES = ['describedBy', 'schema_version', 'samples_core']

SPECIAL_PROPERTIES = ['sample_name', 'unit', 'term_source_id']
