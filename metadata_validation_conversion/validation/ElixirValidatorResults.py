import requests
from metadata_validation_conversion.constants import SAMPLE_CORE_URL, \
    ALLOWED_SAMPLES_TYPES, ALLOWED_EXPERIMENTS_TYPES, EXPERIMENT_CORE_URL
from .helpers import get_record_name, get_validation_results_structure, validate


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
            del type_schema['properties'][core_name]
            for index, record in enumerate(self.json_to_test[name]):
                record_name = get_record_name(record['custom'], index, name)
                tmp = get_validation_results_structure(record_name)
                tmp['core']['errors'] = validate(record[core_name],
                                                 core_schema)
                tmp['type']['errors'] = validate(record, type_schema)
                validation_results[name].append(tmp)
        return validation_results
