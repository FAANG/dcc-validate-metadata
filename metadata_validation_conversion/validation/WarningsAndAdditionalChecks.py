import datetime
from metadata_validation_conversion.constants import ALLOWED_SAMPLES_TYPES, \
    SKIP_PROPERTIES, MISSING_VALUES, SPECIES_BREED_LINKS, \
    ALLOWED_EXPERIMENTS_TYPES, ALLOWED_ANALYSES_TYPES
from metadata_validation_conversion.helpers import get_rules_json
from .get_ontology_text_async import collect_ids
from .helpers import get_record_name, get_validation_results_structure, \
    validate, get_record_structure
import json


class WarningsAndAdditionalChecks:
    def __init__(self, json_to_test, rules_type, structure):
        self.json_to_test = json_to_test
        self.rules_type = rules_type
        self.structure = structure

    def collect_warnings_and_additional_checks(self):
        validation_document = dict()
        if self.rules_type == 'samples':
            allowed_types = ALLOWED_SAMPLES_TYPES
        elif self.rules_type == 'experiments':
            allowed_types = ALLOWED_EXPERIMENTS_TYPES
        else:
            allowed_types = ALLOWED_ANALYSES_TYPES

        # Do additional checks
        for name, url in allowed_types.items():
            if name in self.json_to_test:
                validation_document[name] = self.do_additional_checks(url, name)
        return validation_document

    def do_additional_checks(self, url, name):
        """
        This function will return warning if recommended fields is not present
        in record
        :param url: schema url for this record
        :param name: name of the record
        :return: warnings
        """
        records = self.json_to_test[name]
        structure_to_use = self.structure[name]
        data_to_return = list()
        if name == 'input_dna' or name == 'dna-binding_proteins':
            samples_type_json, samples_core_json, samples_module_json = \
                get_rules_json(url, self.rules_type)
        elif name in ['faang', 'ena', 'eva']:
            samples_type_json = get_rules_json(url, self.rules_type)
            samples_core_json = None
        else:
            samples_type_json, samples_core_json = get_rules_json(
                url, self.rules_type)

        if self.rules_type == 'samples':
            core_name = 'samples_core'
        elif self.rules_type == 'experiments':
            core_name = 'experiments_core'
        else:
            core_name = None

        # Collect list of all fields
        fields = dict()
        json_files = {
            'core': samples_core_json,
            'type': samples_type_json
        }
        try:
            json_files['modular'] = samples_module_json
        except NameError:
            pass
        for field in ['mandatory', 'recommended', 'optional']:
            for json_type, json_file in json_files.items():
                fields.setdefault(field, dict())
                fields[field][json_type] = self.collect_fields(json_file, field)

        # mandatory_type_fields = self.collect_fields(samples_type_json,
        #                                             "mandatory")
        # mandatory_core_fields = self.collect_fields(samples_core_json,
        #                                             "mandatory")
        # recommended_type_fields = self.collect_fields(samples_type_json,
        #                                               "recommended")
        # recommended_core_fields = self.collect_fields(samples_core_json,
        #                                               "recommended")
        # optional_type_fields = self.collect_fields(samples_type_json,
        #                                            "optional")
        # optional_core_fields = self.collect_fields(samples_core_json,
        #                                            "optional")

        ontology_names_type = self.collect_ontology_names(samples_type_json)
        ontology_names_core = self.collect_ontology_names(samples_core_json)
        ontology_ids = collect_ids(records, core_name)

        for index, record in enumerate(records):
            # Get inner issues structure
            record_to_return = get_record_structure(structure_to_use, record)

            if core_name is not None:
                # Check that recommended fields are present for core fields
                self.check_recommended_fields(
                    record[core_name], fields['recommended']['core'],
                    record_to_return[core_name])

                # Check that ontology text is consistent with ontology term for
                # core fields
                self.check_ontology_text(record[core_name], ontology_ids,
                                         record_to_return[core_name],
                                         ontology_names_core)

                # Check that date value is consistent with date units for core
                # fields
                self.check_date_units(record[core_name],
                                      record_to_return[core_name])

                # Check that data has special missing values for core fields
                self.check_missing_values(record[core_name],
                                          record_to_return[core_name],
                                          fields['mandatory']['core'],
                                          fields['recommended']['core'],
                                          fields['optional']['core'])

            # Check that recommended fields are present for type fields
            self.check_recommended_fields(
                record, fields['recommended']['type'], record_to_return)

            # Check that ontology text is consistent with ontology term for
            # type fields
            self.check_ontology_text(record, ontology_ids, record_to_return,
                                     ontology_names_type)

            # Check that date value is consistent with date units for type
            # fields
            self.check_date_units(record, record_to_return)

            # Check that data has special missing values for type fields
            self.check_missing_values(record, record_to_return,
                                      fields['mandatory']['type'],
                                      fields['recommended']['type'],
                                      fields['optional']['type'])
            # TODO: check for module fields

            # check species breeds consistency
            if name == 'organism':
                self.check_breeds(record, record_to_return)

            # Check custom fields for ontology consistence
            self.check_ontology_text(record['custom'], ontology_ids,
                                     record_to_return['custom'])

            data_to_return.append(record_to_return)
        return data_to_return

    @staticmethod
    def collect_fields(json_to_check, type_of_fields):
        """
        This function will return list of recommended fields
        :param json_to_check: json to check for recommended fields
        :param type_of_fields: type of fields to collect
        :return: list with recommended fields
        """
        if json_to_check is None:
            return list()
        collected_fields = list()
        for field_name, field_value in json_to_check['properties'].items():
            if field_name not in SKIP_PROPERTIES:
                if field_value['type'] == 'object':
                    if field_value['properties']['mandatory']['const'] == \
                            type_of_fields:
                        collected_fields.append(field_name)
                elif field_value['type'] == 'array':
                    if field_value['items']['properties']['mandatory'][
                        'const'] == \
                            type_of_fields:
                        collected_fields.append(field_name)
        return collected_fields

    def collect_ontology_names(self, json_to_parse):
        """
        This function will parse json-schema to get all ontology_names
        :param json_to_parse: json-schema to parse
        :return: dict with field name as key and ontology_name as value
        """
        if json_to_parse is None:
            return dict()
        ontology_names_to_return = dict()
        for field_name, field_value in json_to_parse['properties'].items():
            if field_name not in SKIP_PROPERTIES \
                    and field_value['type'] == 'object':
                if self.check_ontology_field(field_value['properties'],
                                             'const'):
                    ontology_names_to_return[field_name] = [
                        field_value['properties']['ontology_name'][
                            'const'].lower()]
                elif self.check_ontology_field(field_value['properties'],
                                               'enum'):
                    ontology_names_to_return[field_name] = [
                        term.lower() for term in
                        field_value['properties']['ontology_name']['enum']]
            elif field_name not in SKIP_PROPERTIES \
                    and field_value['type'] == 'array':
                if self.check_ontology_field(
                        field_value['items']['properties'], 'const'):
                    ontology_names_to_return[field_name] = [
                        field_value['items']['properties']['ontology_name'][
                            'const'].lower()]
                elif self.check_ontology_field(
                        field_value['items']['properties'], 'enum'):
                    ontology_names_to_return[field_name] = [
                        term.lower() for term in
                        field_value['items']['properties']['ontology_name'][
                            'enum']]
        return ontology_names_to_return

    @staticmethod
    def check_ontology_field(dict_to_check, label_to_check):
        """
        This function will test that this dict has ontology terms to check
        :param dict_to_check: dict to check
        :param label_to_check: label to check
        :return: True if this is ontology field and False otherwise
        """
        if 'text' in dict_to_check and 'term' in dict_to_check and \
                label_to_check in dict_to_check['ontology_name']:
            return True
        return False

    @staticmethod
    def check_recommended_fields(record, recommended_fields, record_to_return):
        """
        This function will return warnings when recommended field is not present
        :param record: record to check
        :param recommended_fields: list of recommended fields to check
        :param record_to_return: dict for front-end
        """
        for item in recommended_fields:
            if item not in record:
                record_to_return[item].setdefault('warnings', list())
                record_to_return[item]['warnings'].append(
                    'This item is recommended but was not provided'
                )

    def check_ontology_text(self, record, ontology_ids, record_to_return,
                            ontology_names=None):
        """
        This function will check record for ols consistence
        :param record: record to check
        :param ontology_ids: dict with ols records as values and ols ids as keys
        :param record_to_return: dict with data that goes to front-end
        :param ontology_names: dict of ontology names to use
        """
        for field_name, field_value in record.items():
            if isinstance(field_value, list):
                for i, sub_value in enumerate(field_value):
                    ols_results = self.check_ols(sub_value, ontology_names,
                                                 field_name, ontology_ids)
                    if ols_results is not None:
                        record_to_return[field_name][i].setdefault('warnings',
                                                                   list())
                        record_to_return[field_name][i]['warnings'].append(
                            ols_results
                        )
            else:
                ols_results = self.check_ols(field_value, ontology_names,
                                             field_name, ontology_ids)
                if ols_results is not None:
                    record_to_return[field_name].setdefault('warnings', list())
                    record_to_return[field_name]['warnings'].append(ols_results)

    @staticmethod
    def check_ols(field_value, ontology_names, field_name, ontology_ids):
        """
        This function will check ols for label existence
        :param field_value: dict to check
        :param ontology_names: name to use for check
        :param field_name: name of the field to check
        :param ontology_ids: dict with ols records as values and ols ids as keys
        :return: warnings in str format
        """
        if 'text' in field_value and 'term' in field_value:
            term_label = list()
            for label in ontology_ids[field_value['term']]:
                if ontology_names is not None \
                        and label['ontology_name'].lower() \
                        in ontology_names[field_name]:
                    term_label.append(label['label'].lower())
                elif ontology_names is None:
                    term_label.append(label['label'].lower())
            if len(term_label) == 0:
                return f"Couldn't find label in OLS with these ontology " \
                       f"names: {ontology_names[field_name]}"

            if field_value['text'].lower() not in term_label:
                return f"Provided value '{field_value['text']}' doesn't " \
                       f"precisely match '{term_label[0]}' for term " \
                       f"'{field_value['term']}'"
        return None

    @staticmethod
    def check_date_units(record, record_to_return):
        """
        This function will check that date unit is consistent with data value
        :param record: record to check
        :param record_to_return: dict with data that goes to front-end
        """
        for field_name, field_value in record.items():
            if 'date' in field_name and 'value' in field_value and 'units' in \
                    field_value:
                if field_value['units'] == 'YYYY-MM-DD':
                    units = '%Y-%m-%d'
                elif field_value['units'] == 'YYYY-MM':
                    units = '%Y-%m'
                elif field_value['units'] == 'YYYY':
                    units = '%Y'
                else:
                    continue
                try:
                    datetime.datetime.strptime(field_value['value'], units)
                except ValueError:
                    record_to_return[field_name].setdefault('warnings', list())
                    record_to_return[field_name]['warnings'].append(
                        f"Date units: {field_value['units']} should be "
                        f"consistent with date value: {field_value['value']}"
                    )

    def check_missing_values(self, record, record_to_return,
                             mandatory_fields, recommended_fields,
                             optional_fields, index=None):
        """
        This function will check that data contains special missing values
        :param record: record to check
        :param record_to_return: dict with data that goes to front-end
        :param mandatory_fields: list of mandatory fields
        :param recommended_fields: list of recommended fields
        :param optional_fields: list of optional fields
        :param index: index of data in array
        """
        for field_name, field_value in record.items():
            if isinstance(field_value, list):
                for i, sub_value in enumerate(field_value):
                    self.check_missing_values({field_name: sub_value},
                                              record_to_return,
                                              mandatory_fields,
                                              recommended_fields,
                                              optional_fields, i)
            else:
                for k, v in field_value.items():
                    record_to_return_ref = record_to_return[field_name][index] \
                        if index else record_to_return[field_name]
                    if field_name in mandatory_fields:
                        self.check_single_missing_value(k, v,
                                                        MISSING_VALUES[
                                                            'mandatory'],
                                                        field_name,
                                                        record_to_return_ref)
                    elif field_name in recommended_fields:
                        self.check_single_missing_value(k, v,
                                                        MISSING_VALUES[
                                                            'recommended'],
                                                        field_name,
                                                        record_to_return_ref)
                    elif field_name in optional_fields:
                        self.check_single_missing_value(k, v,
                                                        MISSING_VALUES[
                                                            'optional'],
                                                        field_name,
                                                        record_to_return_ref)

    @staticmethod
    def check_single_missing_value(key, value, missing_values, field_name,
                                   record_to_return):
        """
        This function will check that specific cell contains missing values
        :param key: key that we check
        :param value: value that we check
        :param missing_values: list of missing values to search in
        :param field_name: field name that function currently on
        :param record_to_return: dict with data that goes to front-end
        """
        if value in missing_values['errors']:
            record_to_return.setdefault('errors', list())
            record_to_return['errors'].append(
                f"Field '{key}' of '{field_name}' contains missing value that "
                f"is not appropriate for this field"
            )
        elif value in missing_values['warnings']:
            record_to_return.setdefault('warnings', list())
            record_to_return['warnings'].append(
                f"Field '{key}' of '{field_name}' contains missing value that "
                f"is not appropriate for this field"
            )

    @staticmethod
    def check_breeds(record, record_to_return):
        """
        This function will check consistence between breed and species
        :param record: record to check
        :param record_to_return: dict to send to front-end
        :return:
        """
        organism_term = record['organism']['term']
        schema = {
            "type": "string",
            "graph_restriction": {
                "ontologies": ["obo:lbo"],
                "classes": [f"{SPECIES_BREED_LINKS[organism_term]}"],
                "relations": ["rdfs:subClassOf"],
                "direct": False,
                "include_self": True
            }
        }
        validation_results, _ = validate(record['breed']['term'], schema)
        if len(validation_results) > 0:
            record_to_return['organism'].setdefault('errors', list())
            record_to_return['organism']['errors'].append(
                f"Breed '{record['breed']['text']}' doesn't match the animal "
                f"specie: '{record['organism']['text']}'"
            )
