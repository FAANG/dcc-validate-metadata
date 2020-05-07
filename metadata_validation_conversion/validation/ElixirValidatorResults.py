import requests
from metadata_validation_conversion.constants import SAMPLE_CORE_URL, \
    ALLOWED_SAMPLES_TYPES, ALLOWED_EXPERIMENTS_TYPES, EXPERIMENT_CORE_URL, \
    ALLOWED_ANALYSES_TYPES, CHIP_SEQ_MODULE_RULES, SAMPLE, EXPERIMENT, ANALYSIS
from .helpers import validate, get_record_structure


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
        if self.rules_type == SAMPLE:
            record_type = ALLOWED_SAMPLES_TYPES
            core_name = 'samples_core'
            core_url = SAMPLE_CORE_URL
        elif self.rules_type == ANALYSIS:
            record_type = ALLOWED_ANALYSES_TYPES
            core_name = None
            core_url = None
        elif self.rules_type == EXPERIMENT:
            record_type = ALLOWED_EXPERIMENTS_TYPES
            core_name = 'experiments_core'
            core_url = EXPERIMENT_CORE_URL

        core_schema = requests.get(core_url).json() if core_url else None
        validation_document = dict()
        for name, url in record_type.items():
            if name in self.json_to_test:
                validation_document.setdefault(name, list())
                structure_to_use = self.structure[name]
                type_schema = requests.get(url).json()
                module_schema = None
                module_name = None
                if name in CHIP_SEQ_MODULE_RULES:
                    module_schema = requests.get(CHIP_SEQ_MODULE_RULES[name])
                    module_name = name.split("chip-seq_")[-1]
                # in JSON schema, the core ruleset is defined by reference
                if core_name:
                    del type_schema['properties'][core_name]
                # iterate the records
                for index, record in enumerate(self.json_to_test[name]):
                    record_to_return = get_record_structure(
                        structure_to_use, record)
                    if core_schema:
                        errors, paths = validate(record[core_name], core_schema)
                        self.attach_errors(
                            record_to_return, errors, paths, core_name)
                    errors, paths = validate(record, type_schema)
                    self.attach_errors(record_to_return, errors, paths)
                    if module_schema:
                        errors, paths = validate(
                            record[module_name], module_schema)
                        self.attach_errors(
                            record_to_return, errors, paths, module_name)
                    validation_document[name].append(record_to_return)
        return validation_document

    @staticmethod
    def attach_errors(record_to_return, errors, paths, additional_field=None):
        """
        This function will add all errors to document
        :param record_to_return: record to add errors to
        :param errors: list of errors
        :param paths: list of paths of errors
        :param additional_field: could be core field or modular field
        """
        for i, error in enumerate(errors):
            keys = paths[i].split('.')
            if additional_field:
                record_to_return[additional_field][keys[1]].setdefault(
                    'errors', list())
                record_to_return[additional_field][keys[1]]['errors'].append(
                    error)
            else:
                record_to_return[keys[1]].setdefault('errors', list())
                record_to_return[keys[1]]['errors'].append(error)
