import requests
from metadata_validation_conversion.constants import SAMPLE_CORE_URL, \
    ALLOWED_SAMPLES_TYPES, ALLOWED_EXPERIMENTS_TYPES, EXPERIMENT_CORE_URL, \
    CHIP_SEQ_INPUT_DNA_URL, CHIP_SEQ_DNA_BINDING_PROTEINS_URL
from .helpers import get_record_name, get_validation_results_structure, validate
import json


class ElixirValidatorResults:
    def __init__(self, json_to_test, rules_type):
        self.json_to_test = json_to_test
        self.rules_type = rules_type

    def run_validation(self):
        """
        This function will run validation using Elixir Validator
        :return: results of validation
        """
        if self.rules_type == 'samples':
            record_type = ALLOWED_SAMPLES_TYPES
            core_name = 'samples_core'
            core_url = SAMPLE_CORE_URL
        else:
            record_type = ALLOWED_EXPERIMENTS_TYPES
            core_name = 'experiments_core'
            core_url = EXPERIMENT_CORE_URL

        core_schema = requests.get(core_url).json()
        validation_results = dict()
        for name, url in record_type.items():
            validation_results.setdefault(name, list())
            type_schema = requests.get(url).json()
            module_schema = None
            if name == 'chip-seq_input_dna':
                module_schema = requests.get(CHIP_SEQ_INPUT_DNA_URL).json()
                module_name = 'input_dna'
            if name == 'chip-seq_dna-binding_proteins':
                module_schema = requests.get(
                    CHIP_SEQ_DNA_BINDING_PROTEINS_URL).json()
                module_name = 'dna-binding_proteins'
            del type_schema['properties'][core_name]
            for index, record in enumerate(self.json_to_test[name]):
                record_name = get_record_name(record['custom'], index, name)
                tmp = get_validation_results_structure(
                    record_name, module_schema is not None)
                tmp['core']['errors'] = validate(record[core_name],
                                                 core_schema)
                tmp['type']['errors'] = validate(record, type_schema)
                if module_schema:
                    tmp['module']['errors'] = validate(record[module_name],
                                                       module_schema)
                validation_results[name].append(tmp)
        return validation_results
