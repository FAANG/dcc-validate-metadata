import requests
from metadata_validation_conversion.constants import SAMPLE_CORE_URL, \
    ALLOWED_SAMPLES_TYPES, ALLOWED_EXPERIMENTS_TYPES, EXPERIMENT_CORE_URL, \
    CHIP_SEQ_INPUT_DNA_URL, CHIP_SEQ_DNA_BINDING_PROTEINS_URL, \
    ALLOWED_ANALYSES_TYPES
from .helpers import get_record_name, get_validation_results_structure, \
    validate, get_record_structure
import json


class ElixirValidatorResults:
    def __init__(self, json_to_test, rules_type, structure):
        self.json_to_test = json_to_test
        self.rules_type = rules_type
        self.structure = structure

    def run_validation(self):
        """
        This function will run validation using Elixir Validator
        :return: results of validation
        """
        if self.rules_type == 'samples':
            record_type = ALLOWED_SAMPLES_TYPES
            core_name = 'samples_core'
            core_url = SAMPLE_CORE_URL
        elif self.rules_type == 'analyses':
            record_type = ALLOWED_ANALYSES_TYPES
            core_name = None
            core_url = None
        else:
            record_type = ALLOWED_EXPERIMENTS_TYPES
            core_name = 'experiments_core'
            core_url = EXPERIMENT_CORE_URL

        core_schema = requests.get(core_url).json() if core_url else None
        validation_results = dict()
        validation_document = dict()
        for name, url in record_type.items():
            if name in self.json_to_test:
                validation_results.setdefault(name, list())
                validation_document.setdefault(name, list())
                structure_to_use = self.structure[name]
                type_schema = requests.get(url).json()
                module_schema = None
                if name == 'chip-seq_input_dna':
                    module_schema = requests.get(CHIP_SEQ_INPUT_DNA_URL).json()
                    module_name = 'input_dna'
                if name == 'chip-seq_dna-binding_proteins':
                    module_schema = requests.get(
                        CHIP_SEQ_DNA_BINDING_PROTEINS_URL).json()
                    module_name = 'dna-binding_proteins'
                if core_name:
                    del type_schema['properties'][core_name]
                for index, record in enumerate(self.json_to_test[name]):
                    record_name = get_record_name(record, index, name)
                    tmp = get_validation_results_structure(
                        record_name, module_schema is not None)
                    record_to_return = get_record_structure(
                        structure_to_use, record)
                    if core_schema:
                        tmp['core']['errors'], paths = validate(
                            record[core_name], core_schema)
                        for i, error in enumerate(tmp['core']['errors']):
                            keys = paths[i].split('.')
                            record_to_return[core_name][keys[1]].setdefault(
                                'errors', list())
                            record_to_return[core_name][keys[1]][
                                'errors'].append(error)
                    # TODO: add module errors
                    tmp['type']['errors'], paths = validate(record, type_schema)
                    for i, error in enumerate(tmp['type']['errors']):
                        keys = paths[i].split('.')
                        record_to_return[keys[1]].setdefault('errors', list())
                        record_to_return[keys[1]]['errors'].append(error)
                    if module_schema:
                        tmp['module']['errors'] = validate(record[module_name],
                                                           module_schema)
                    validation_results[name].append(tmp)
                    validation_document[name].append(record_to_return)
        validation_document.setdefault('table', True)
        return validation_results, validation_document
