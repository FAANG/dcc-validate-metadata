import requests
from metadata_validation_conversion.constants import SAMPLE_CORE_URL, \
    ALLOWED_RECORD_TYPES
from .helpers import get_record_name, get_validation_results_structure, validate


class ElixirValidatorResults:
    def __init__(self, json_to_test):
        self.json_to_test = json_to_test

    def run_validation(self):
        """
        This function will run validation using Elixir Validator
        :return: results of validation
        """
        core_schema = requests.get(SAMPLE_CORE_URL).json()
        validation_results = dict()
        for name, url in ALLOWED_RECORD_TYPES.items():
            validation_results.setdefault(name, list())
            type_schema = requests.get(url).json()
            del type_schema['properties']['samples_core']
            for index, record in enumerate(self.json_to_test[name]):
                record_name = get_record_name(record['custom'], index, name)
                tmp = get_validation_results_structure(record_name)
                tmp['core']['errors'] = validate(record['samples_core'],
                                                 core_schema)
                tmp['type']['errors'] = validate(record, type_schema)
                validation_results[name].append(tmp)
        return validation_results
