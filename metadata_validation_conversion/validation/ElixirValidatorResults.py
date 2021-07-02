import requests
from metadata_validation_conversion.constants import SAMPLE_CORE_URL, \
    ALLOWED_SAMPLES_TYPES, ALLOWED_EXPERIMENTS_TYPES, EXPERIMENT_CORE_URL, \
    ALLOWED_ANALYSES_TYPES, MODULE_RULES
from .helpers import validate, get_record_structure
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
        validation_document = dict()
        for name, url in record_type.items():
            if name in self.json_to_test:
                validation_document.setdefault(name, list())
                structure_to_use = self.structure[name]
                type_schema = requests.get(url).json()
                module_schema = None
                module_name = None
                if name in MODULE_RULES:
                    module_schema = requests.get(MODULE_RULES[name]).json()
                    if 'chip-seq' in name:
                        module_name = name.split("chip-seq_")[-1]
                    else:
                        module_name = name

                # Elixir validator complains about links
                if core_name:
                    del type_schema['properties'][core_name]

                # Elixir validator complains about duplicated values in enum
                if 'experiment_target' in type_schema['properties']:
                    del type_schema['properties']['experiment_target'][
                        'properties']['ontology_name']

                # Elixir validator complains about links
                if 'dna-binding_proteins' in type_schema['properties']:
                    del type_schema['properties']['dna-binding_proteins']

                # Elixir validator complains about links
                if 'input_dna' in type_schema['properties']:
                    del type_schema['properties']['input_dna']

                for index, record in enumerate(self.json_to_test[name]):
                    record_to_return = get_record_structure(
                        structure_to_use, record, module_name)
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

    def attach_errors(self, record_to_return, errors, paths,
                      additional_field=None):
        """
        This function will add all errors to document
        :param record_to_return: record to add errors to
        :param errors: list of errors
        :param paths: list of paths of errors
        :param additional_field: could be core field or modular field
        """
        for i, error in enumerate(errors):
            if 'root of document' in error:
                key = error.split("'")[1]
                self.update_record_to_return(record_to_return, key, error,
                                             additional_field=additional_field)
                continue
            keys = paths[i].split('.')
            # Check that returned path was for fields that allow to have
            # multiple values
            if '[' in keys[0]:
                key = keys[0].split('[')[1].split(']')[0]
                key = key.split("'")[1]
                self.update_record_to_return(record_to_return, key, error,
                                             additional_field=additional_field)
                continue
            if '[' in keys[1]:
                # parsing values like 'health_status[0]'
                key = keys[1].split('[')[0]
                additional_key = int(keys[1].split('[')[-1].split(']')[0])
                self.update_record_to_return(record_to_return, key, error,
                                             additional_key=additional_key,
                                             additional_field=additional_field)
            else:
                key = keys[1]
                self.update_record_to_return(record_to_return, key, error,
                                             additional_field=additional_field)

    @staticmethod
    def update_record_to_return(record_to_return, key, error,
                                additional_key=None, additional_field=None):
        """
        This function will add error to record_to_return
        :param record_to_return: record to update
        :param key: key of error inside record_to_return
        :param error: errors message
        :param additional_key: index of field inside record_to_return
        :param additional_field: might be core, etc..
        :return:
        """
        if additional_key is not None and additional_field is not None:
            pointer = record_to_return[additional_field][key][additional_key]
        elif additional_key is not None and additional_field is None:
            pointer = record_to_return[key][additional_key]
        elif additional_key is None and additional_field is not None:
            pointer = record_to_return[additional_field][key]
        else:
            pointer = record_to_return[key]
        if isinstance(pointer, list):
            for second_pointer in pointer:
                second_pointer.setdefault('errors', list())
                second_pointer['errors'].append(error)
        else:
            pointer.setdefault('errors', list())
            pointer['errors'].append(error)
