from metadata_validation_conversion.constants import ALLOWED_SAMPLES_TYPES, \
    ALLOWED_RELATIONSHIPS
from metadata_validation_conversion.helpers import convert_to_snake_case
from .helpers import get_record_name, get_validation_results_structure, \
    get_record_structure
from .get_biosample_data_async import fetch_biosample_data_for_ids
import json


class RelationshipsIssues:
    def __init__(self, json_to_test, structure):
        self.json_to_test = json_to_test
        self.structure = structure

    def collect_relationships_issues(self):
        relationships = dict()
        biosamples_ids_to_call = set()
        validation_document = dict()

        # In first iteration need to collect all relationships
        for name, url in ALLOWED_SAMPLES_TYPES.items():
            if name in self.json_to_test:
                new_relationships, biosample_ids, validation_document[name] = \
                    self.collect_relationships(name)
                relationships.update(new_relationships)
                biosamples_ids_to_call.update(biosample_ids)
        biosample_data = fetch_biosample_data_for_ids(biosamples_ids_to_call)
        return self.check_relationships(relationships, biosample_data,
                                        validation_document)

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
            record_to_return = get_record_structure(structure_to_use, record)
            record_name = get_record_name(record, index, name)
            relationships.setdefault(record_name, dict())
            relationship_name = 'child_of' if name == 'organism' else \
                'derived_from'
            if relationship_name in record and isinstance(
                    record[relationship_name], list):
                tmp = list()
                for child in record[relationship_name]:
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
            if relationship_name == 'child_of':
                relationships[record_name]['organism'] = record['organism'][
                    'text']
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
        issues_to_return = dict()
        for k, v in relationships.items():
            name = convert_to_snake_case(v['material'])
            issues_to_return.setdefault(name, list())
            tmp = get_validation_results_structure(k)
            record_to_return = self.find_record(validation_document, name, k)
            relationship_name = 'child_of' if name == 'organism' else \
                'derived_from'
            relationship_to_return = record_to_return[relationship_name]
            if 'relationships' in v:
                errors = list()
                for relation in v['relationships']:
                    if relation not in relationships and relation not in \
                            biosample_data:
                        errors.append(
                            f"Relationships part: no entity '{relation}' "
                            f"found")
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
                tmp['type']['errors'].extend(errors)
            issues_to_return[name].append(tmp)
        validation_document.setdefault('table', True)
        return issues_to_return, validation_document

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
                if entity['value'] == relation:
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
        if current_organism_name in relation_organism_value['relationships']:
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
