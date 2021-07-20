import datetime
from metadata_validation_conversion.constants import ALLOWED_SAMPLES_TYPES, \
    SKIP_PROPERTIES, MISSING_VALUES, SPECIES_BREED_LINKS, \
    ALLOWED_EXPERIMENTS_TYPES, ALLOWED_ANALYSES_TYPES, \
    CHIP_SEQ_INPUT_DNA_URL, CHIP_SEQ_DNA_BINDING_PROTEINS_URL, \
    TELEOSTEI_EMBRYO_URL, TELEOSTEI_POST_HATCHING_URL
from metadata_validation_conversion.helpers import get_rules_json
from .get_ontology_text_async import collect_ids
from .helpers import validate, get_record_structure
import requests
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
        if name == 'chip-seq_input_dna':
            samples_type_json, samples_core_json, samples_module_json = \
                get_rules_json(url, self.rules_type, CHIP_SEQ_INPUT_DNA_URL)
            module_name = name.split("chip-seq_")[-1]
        elif name == 'chip-seq_dna-binding_proteins':
            samples_type_json, samples_core_json, samples_module_json = \
                get_rules_json(url, self.rules_type,
                               CHIP_SEQ_DNA_BINDING_PROTEINS_URL)
            module_name = name.split("chip-seq_")[-1]
        elif name == 'teleostei_embryo':
            samples_type_json, samples_core_json, samples_module_json = \
                get_rules_json(url, self.rules_type, TELEOSTEI_EMBRYO_URL)
            module_name = name
        elif name == 'teleostei_post-hatching':
            samples_type_json, samples_core_json, samples_module_json = \
                get_rules_json(url, self.rules_type,
                               TELEOSTEI_POST_HATCHING_URL)
            module_name = name
        elif name in ['faang', 'ena', 'eva']:
            samples_type_json = get_rules_json(url, self.rules_type)
            samples_core_json, samples_module_json, module_name = \
                None, None, None
        else:
            samples_type_json, samples_core_json = get_rules_json(
                url, self.rules_type)
            samples_module_json, module_name = None, None

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
            json_files['module'] = samples_module_json
        except NameError:
            pass
        for field in ['mandatory', 'recommended', 'optional']:
            for json_type, json_file in json_files.items():
                fields.setdefault(field, dict())
                fields[field][json_type] = self.collect_fields(json_file, field)

        ontology_names_type = self.collect_ontology_names(samples_type_json)
        ontology_names_core = self.collect_ontology_names(samples_core_json)
        ontology_names_module = self.collect_ontology_names(samples_module_json)

        ontology_ids = collect_ids(records, core_name, module_name)

        for index, record in enumerate(records):
            # Get inner issues structure
            record_to_return = get_record_structure(structure_to_use, record,
                                                    module_name)

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
            if module_name is not None:
                # Check that recommended fields are present for core fields
                self.check_recommended_fields(
                    record[module_name], fields['recommended']['module'],
                    record_to_return[module_name])

                # Check that ontology text is consistent with ontology term for
                # core fields
                self.check_ontology_text(record[module_name], ontology_ids,
                                         record_to_return[module_name],
                                         ontology_names_module)

                # Check that date value is consistent with date units for core
                # fields
                self.check_date_units(record[module_name],
                                      record_to_return[module_name])

                # Check that data has special missing values for core fields
                self.check_missing_values(record[module_name],
                                          record_to_return[module_name],
                                          fields['mandatory']['module'],
                                          fields['recommended']['module'],
                                          fields['optional']['module'])

            # check species breeds consistency
            if name == 'organism':
                self.check_breeds(record, record_to_return)

            # Check custom fields for ontology consistence
            self.check_ontology_text(record['custom'], ontology_ids,
                                     record_to_return['custom'])

            # check linked Biosample
            if self.rules_type == 'experiments' or self.rules_type == 'analyses':
                self.check_biosample_for_ena(record, record_to_return)

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
                if isinstance(record_to_return[item], list):
                    for row in record_to_return[item]:
                        row.setdefault('warnings', list())
                        row['warnings'].append(
                            'This item is recommended but was not provided')
                else:
                    record_to_return[item].setdefault('warnings', list())
                    record_to_return[item]['warnings'].append(
                        'This item is recommended but was not provided')

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

            # Use str in case user provided number
            if str(field_value['text']).lower() not in term_label:
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
                    record_to_return[field_name].setdefault('errors', list())
                    record_to_return[field_name]['errors'].append(
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
            if field_name in SKIP_PROPERTIES:
                continue
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
                        if index is not None else record_to_return[field_name]
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
        try:
            organism_term = record['organism']['term']
        except KeyError:
            return
        if organism_term not in SPECIES_BREED_LINKS:
            return
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

    def check_biosample_for_ena(self, record, record_to_return):
        '''
        This function will check that the linked Biosample is not organism,
        for ENA submission (experiements and analyses)
        :param record: record to check
        :param record_to_return: dict to send to front-end
        :return:
        '''
        for field_name, field_value in record.items():
            # for experiments
            if 'sample_descriptor' in field_value:
                if self.biosample_is_not_specimen(record_to_return[field_name]['sample_descriptor']['value']):
                    record_to_return[field_name]['sample_descriptor'].setdefault('errors', list())
                    record_to_return[field_name]['sample_descriptor']['errors'].append(
                        "Linked Biosample should be a specimen")
            # for analyses
            elif field_name == 'samples':
                if isinstance(record['samples'], list):
                    for index, sample in enumerate(record['samples']):
                        if self.biosample_is_not_specimen(record_to_return['samples'][index]['value']):
                            record_to_return['samples'][index].setdefault('errors', list())
                            record_to_return['samples'][index]['errors'].append(
                            "Linked Biosample should be a specimen")
                else:
                    if self.biosample_is_not_specimen(record_to_return['samples']['value']):
                        record_to_return['samples'].setdefault('errors', list())
                        record_to_return['samples']['errors'].append(
                        "Linked Biosample should be a specimen")
            # for analyses
            elif 'samples' in field_value:
                if isinstance(record[field_name]['samples'], list):
                    for index, sample in enumerate(record[field_name]['samples']):
                        if self.biosample_is_not_specimen(record_to_return[field_name]['samples'][index]['value']):
                            record_to_return[field_name]['samples'][index].setdefault('errors', list())
                            record_to_return[field_name]['samples'][index]['errors'].append(
                            "Linked Biosample should be a specimen")
                else:
                    if self.biosample_is_not_specimen(record_to_return[field_name]['samples']['value']):
                        record_to_return[field_name]['samples'].setdefault('errors', list())
                        record_to_return[field_name]['samples']['errors'].append(
                        "Linked Biosample should be a specimen")

    @staticmethod
    def biosample_is_not_specimen(biosample_id):
        '''
        Check if Biosample associated with the id is organism,
        by querying biosample API
        :param biosample_id: id to query biosamples API and get info
        :return: boolean
        '''
        url = 'https://www.ebi.ac.uk/biosamples/samples/' + biosample_id
        res = requests.get(url)
        try:
            data = json.loads(res.content)
            for material in data['characteristics']['material']:
                if material['text'] == 'organism':
                    return True
            return False
        except:
            return True
