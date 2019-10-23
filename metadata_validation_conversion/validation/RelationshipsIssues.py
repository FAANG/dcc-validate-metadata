from metadata_validation_conversion.constants import ALLOWED_RECORD_TYPES, \
    ALLOWED_RELATIONSHIPS
from metadata_validation_conversion.helpers import convert_to_snake_case
from .helpers import get_record_name, get_validation_results_structure
from .get_biosample_data_async import fetch_biosample_data_for_ids


class RelationshipsIssues:
    def __init__(self, json_to_test):
        self.json_to_test = json_to_test

    def collect_relationships_issues(self):
        relationships = dict()
        biosamples_ids_to_call = set()

        # In first iteration need to collect all relationships
        for name, url in ALLOWED_RECORD_TYPES.items():
            new_relationships, biosample_ids = self.collect_relationships(name)
            relationships.update(new_relationships)
            biosamples_ids_to_call.update(biosample_ids)
        biosample_data = fetch_biosample_data_for_ids(biosamples_ids_to_call)
        relationships.update(biosample_data)
        return self.check_relationships(relationships)

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
        records = self.json_to_test[name]
        for index, record in enumerate(records):
            record_name = get_record_name(record['custom'], index, name)
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
        return relationships, biosample_ids

    def check_relationships(self, relationships):
        """
        This function will check relationships values
        :param relationships: relationships to check
        :return: issues in dict format
        """
        issues_to_return = dict()
        for k, v in relationships.items():
            name = convert_to_snake_case(v['material'])
            issues_to_return.setdefault(name, list())
            tmp = get_validation_results_structure(k)
            if 'relationships' in v:
                errors = list()
                for relation in v['relationships']:
                    if relation not in relationships:
                        errors.append(
                            f"Relationships part: no entity '{relation}' "
                            f"found")
                    else:
                        current_material = convert_to_snake_case(v['material'])
                        relation_material = convert_to_snake_case(
                            relationships[relation]['material'])
                        if current_material == 'organism' and \
                                relation_material == 'organism':
                            self.check_parents(k, v, relation,
                                               relationships[relation], errors)
                        allowed_relationships = ALLOWED_RELATIONSHIPS[
                            current_material]
                        if relation_material not in allowed_relationships:
                            errors.append(
                                f"Relationships part: referenced entity '"
                                f"{relation}' does not match condition '"
                                f"should be "
                                f"{' or '.join(allowed_relationships)}'")
                tmp['type']['errors'].extend(errors)
            issues_to_return[name].append(tmp)
        return issues_to_return

    @staticmethod
    def check_parents(current_organism_name, current_organism_value,
                      relation_organism_name, relation_organism_value,
                      results_holder):
        """
        This function will perform parent-child relationships checks
        :param current_organism_name: name of current organism
        :param current_organism_value: values of current organism
        :param relation_organism_name: name of relation organism
        :param relation_organism_value: values of relation organism
        :param results_holder: variable to save results to
        """
        if current_organism_value['organism'] != \
                relation_organism_value['organism']:
            results_holder.append(
                f"Relationships part: the specie of the child "
                f"'{current_organism_value['organism']}' doesn't match the "
                f"specie of the parent '{relation_organism_value['organism']}'")
        if current_organism_name in relation_organism_value['relationships']:
            results_holder.append(f"Relationships part: parent "
                                  f"'{relation_organism_name}' is listing "
                                  f"the child as its parent")
