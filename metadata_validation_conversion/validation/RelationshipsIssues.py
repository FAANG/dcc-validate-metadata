from metadata_validation_conversion.constants import ALLOWED_SAMPLES_TYPES, \
    ALLOWED_RELATIONSHIPS
from metadata_validation_conversion.helpers import convert_to_snake_case
from .helpers import get_record_name, get_record_structure
from .get_biosample_data_async import fetch_biosample_data_for_ids
import requests
import json

class RelationshipsIssues:
    def __init__(self, json_to_test, validation_type, structure):
        self.json_to_test = json_to_test
        self.validation_type = validation_type
        self.structure = structure

    def collect_relationships_issues(self):
        relationships = dict()
        biosamples_ids_to_call = set()
        validation_document = dict()

        # In first iteration need to collect all relationships
        if self.validation_type == 'samples':
            for name, url in ALLOWED_SAMPLES_TYPES.items():
                if name in self.json_to_test:
                    new_relationships, biosample_ids, validation_document[name] = \
                        self.collect_relationships(name)
                    relationships.update(new_relationships)
                    biosamples_ids_to_call.update(biosample_ids)
            biosample_data = fetch_biosample_data_for_ids(biosamples_ids_to_call)
            return self.check_relationships(relationships, biosample_data,
                                            validation_document)
        elif self.validation_type == 'experiments':
            return self.contextual_validation()

    def contextual_validation(self):
        """
        This function will perform contexual validation for experiments
        :return: record dicts with errors
        """
        if 'chip-seq_dna-binding_proteins' in self.json_to_test:
            records = self.json_to_test['chip-seq_dna-binding_proteins']
            for index, record in enumerate(records):
                if 'dna-binding_proteins' in record and \
                    'control_experiment' in record['dna-binding_proteins']:
                    control_exp = record['dna-binding_proteins']['control_experiment']['value']
                    if not self.find_control_experiment(control_exp):
                        error = f"Control experiment {control_exp} " \
                            f"not found in this submission or in ENA"
                        self.add_errors_to_relationships(
                            record['dna-binding_proteins']['control_experiment'], error, 'control_experiment')
        return self.json_to_test

    def find_control_experiment(self, exp):
        """
        This function checks whether control experiment for ChIP-seq 
        DNA-binding proteins experiments exists within the submission 
        (check alias) or in ENA (check accession)
        :return: boolean indicating whether or not the experiment exists
        """
        records = self.json_to_test['chip-seq_dna-binding_proteins']
        # find control experiment in current submission
        for index, record in enumerate(records):
            if record['custom']['experiment_alias']['value'] == exp:
                return True
        # find control experiment in existing ENA submission
        r = requests.get(f'https://www.ebi.ac.uk/ena/browser/api/summary/{exp}')
        if r.status_code == 200:
            res = json.loads(r.content)
            if int(res['total']) > 0:
                return True
        return False

    def collect_relationships(self, name):
        """
        This function will collect information about existing relationships and
        material types for each record
        :param name: name of the record, ex. 'organism'
        :return: dict with record_named as key and relationships + material as
        values
        """
        relationships = dict()
        biosample_ids = set()
        data_to_return = list()
        records = self.json_to_test[name]
        structure_to_use = self.structure[name]
        for index, record in enumerate(records):
            module_name = None
            if name in ['teleostei_embryo', 'teleostei_post-hatching']:
                module_name = name
            record_to_return = get_record_structure(structure_to_use, record,
                                                    module_name)
            record_name = get_record_name(record, index, name)
            relationships.setdefault(record_name, dict())
            relationship_name = 'child_of' if name == 'organism' else \
                'derived_from'
            if relationship_name in record and isinstance(
                    record[relationship_name], list):
                tmp = list()
                for child in record[relationship_name]:
                    child['value'] = str(child['value'])
                    if 'SAM' in child['value']:
                        biosample_ids.add(child['value'])
                    tmp.append(child['value'])
                relationships[record_name]['relationships'] = tmp
            elif relationship_name in record and isinstance(
                    record[relationship_name], dict):
                if 'SAM' in record[relationship_name]['value']:
                    biosample_ids.add(record[relationship_name]['value'])
                relationships[record_name]['relationships'] = [
                    record[relationship_name]['value']]
            relationships[record_name]['material'] = \
                record['samples_core']['material']['text']
            if module_name:
                relationships[record_name]['material'] = module_name
            if relationship_name == 'child_of':
                try:
                    relationships[record_name]['organism'] = \
                        record['organism']['text']
                except KeyError:
                    pass
            data_to_return.append(record_to_return)
        return relationships, biosample_ids, data_to_return

    def check_relationships(self, relationships, biosample_data,
                            validation_document):
        """
        This function will check relationships values
        :param relationships: relationships to check
        :param biosample_data: relationships to check from biosamples
        :param validation_document: document to send to front-end
        :return: issues in dict format
        """
        for k, v in relationships.items():
            name = convert_to_snake_case(v['material'])
            record_to_return = self.find_record(validation_document, name, k)
            relationship_name = 'child_of' if name == 'organism' else \
                'derived_from'
            relationship_to_return = record_to_return[relationship_name]
            if 'relationships' in v:
                errors = list()
                for relation in v['relationships']:
                    if relation not in relationships and relation not in \
                            biosample_data:
                        errors.append(f"Relationships part: no entity "
                                      f"'{relation}' found")
                        self.add_errors_to_relationships(
                            relationship_to_return, errors[-1], relation)
                    else:
                        if relation in relationships:
                            relationships_to_check = relationships
                        elif relation in biosample_data:
                            relationships_to_check = biosample_data
                        current_material = convert_to_snake_case(v['material'])
                        relation_material = convert_to_snake_case(
                            relationships_to_check[relation]['material'])
                        if current_material == 'organism' and \
                                relation_material == 'organism':
                            self.check_parents(
                                k, v, relation,
                                relationships_to_check[relation],
                                errors, relationship_to_return)
                        allowed_relationships = ALLOWED_RELATIONSHIPS[
                            current_material]
                        if relation_material not in allowed_relationships:
                            errors.append(
                                f"Relationships part: referenced entity '"
                                f"{relation}' does not match condition '"
                                f"should be "
                                f"{' or '.join(allowed_relationships)}'")
                            self.add_errors_to_relationships(
                                relationship_to_return, errors[-1], relation)
        return validation_document

    @staticmethod
    def add_errors_to_relationships(relationship_to_return, error, relation):
        """
        This function will add relationships issues to data that goes to
        front-end
        :param relationship_to_return: data that goes to front-end
        :param error: error to add
        :param relation: sample name
        :return:
        """
        if isinstance(relationship_to_return, dict):
            relationship_to_return.setdefault('errors', list())
            relationship_to_return['errors'].append(error)
        else:
            for index, entity in enumerate(relationship_to_return):
                if str(entity['value']) == relation:
                    relationship_to_return[index].setdefault('errors', list())
                    relationship_to_return[index]['errors'].append(error)

    def check_parents(self, current_organism_name, current_organism_value,
                      relation_organism_name, relation_organism_value,
                      results_holder, relationship_to_return):
        """
        This function will perform parent-child relationships checks
        :param current_organism_name: name of current organism
        :param current_organism_value: values of current organism
        :param relation_organism_name: name of relation organism
        :param relation_organism_value: values of relation organism
        :param results_holder: variable to save results to
        :param relationship_to_return: relationships that goes to front-end
        """
        if current_organism_value['organism'] != \
                relation_organism_value['organism']:
            results_holder.append(
                f"Relationships part: the specie of the child "
                f"'{current_organism_value['organism']}' doesn't match the "
                f"specie of the parent '{relation_organism_value['organism']}'")
            self.add_errors_to_relationships(
                relationship_to_return, results_holder[-1],
                relation_organism_name)
        if 'relationships' in relation_organism_value and  \
                current_organism_name in \
                relation_organism_value['relationships']:
            results_holder.append(f"Relationships part: parent "
                                  f"'{relation_organism_name}' is listing "
                                  f"the child as its parent")
            self.add_errors_to_relationships(
                relationship_to_return, results_holder[-1],
                relation_organism_name
            )

    @staticmethod
    def find_record(validation_document, material, name):
        """
        This function will find particular record to update from whole document
        :param validation_document: document to search in
        :param material: material to use
        :param name: name of the record
        :return: record to update relationships
        """
        for record in validation_document[material]:
            if record['custom']['sample_name']['value'] == name:
                return record
