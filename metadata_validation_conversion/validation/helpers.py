import requests
import datetime
import json
from metadata_validation_conversion.helpers import get_samples_json, \
    convert_to_snake_case
from metadata_validation_conversion.constants import SKIP_PROPERTIES, \
    ALLOWED_RELATIONSHIPS
from .get_ontology_text_async import collect_ids


def validate(data, schema):
    """
    This function will send data to elixir-validator and collect all errors
    :param data: data to validate in JSON format
    :param schema: schema to validate against
    :return: list of error messages
    """
    json_to_send = {
        'schema': schema,
        'object': data
    }
    response = requests.post(
        'http://localhost:3020/validate', json=json_to_send).json()
    validation_errors = list()
    if 'validationErrors' in response and len(response['validationErrors']) > 0:
        for error in response['validationErrors']:
            validation_errors.append(error['userFriendlyMessage'])
    return validation_errors


def collect_recommended_fields(json_to_check):
    """
    This function will return list of recommended fields
    :param json_to_check: json to check for recommended fields
    :return: list with recommended fields
    """
    recommended_fields = list()
    for field_name, field_value in json_to_check['properties'].items():
        if field_name not in SKIP_PROPERTIES:
            if field_value['type'] == 'object':
                if field_value['properties']['mandatory']['const'] == \
                        'recommended':
                    recommended_fields.append(field_name)
            elif field_value['type'] == 'array':
                if field_value['items']['properties']['mandatory']['const'] == \
                        'recommended':
                    recommended_fields.append(field_name)
    return recommended_fields


def check_item_is_present(dict_to_check, list_of_items):
    """
    This function will collect all field names that are not in data
    :param dict_to_check: data to check
    :param list_of_items: list of items to search in data
    :return: list of items that are not in data
    """
    warnings = list()
    for item in list_of_items:
        if item not in dict_to_check:
            warnings.append(item)
    return warnings


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
        term_label = set()
        for label in ontology_ids[field_value['term']]:
            if ontology_names is not None and label['ontology_name'].lower() \
                    in ontology_names[field_name]:
                term_label.add(label['label'].lower())
            elif ontology_names is None:
                term_label.add(label['label'].lower())
        if len(term_label) == 0:
            return f"Couldn't find label in OLS with these ontology names: " \
                   f"{ontology_names[field_name]}"

        if field_value['text'].lower() not in term_label:
            return f"Provided value '{field_value['text']}' doesn't " \
                   f"precisely match '{' or '.join(term_label)}' " \
                   f"for term '{field_value['term']}'"
    return None


def check_ontology_text(record, ontology_ids, ontology_names=None):
    """
    This function will check record for ols consistence
    :param record: record to check
    :param ontology_ids: dict with ols records as values and ols ids as keys
    :param ontology_names: dict of ontology names to use
    :return: list of warnings related to ontology inconsistence
    """
    ontology_warnings = list()
    for field_name, field_value in record.items():
        if isinstance(field_value, list):
            for sub_value in field_value:
                ols_results = check_ols(sub_value, ontology_names, field_name,
                                        ontology_ids)
                if ols_results is not None:
                    ontology_warnings.append(ols_results)
        else:
            ols_results = check_ols(field_value, ontology_names, field_name,
                                    ontology_ids)
            if ols_results is not None:
                ontology_warnings.append(ols_results)

    return ontology_warnings


def check_date_units(record):
    date_units_warnings = list()
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
                date_units_warnings.append(f"Date units: "
                                           f"{field_value['units']} should be "
                                           f"consistent with date value: "
                                           f"{field_value['value']}")
    return date_units_warnings


def check_breeds():
    pass


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
        results_holder.append(f"Relationships part: the specie of the child "
                              f"'{current_organism_value['organism']}' doesn't "
                              f"match the specie of the parent "
                              f"'{relation_organism_value['organism']}'")
    if current_organism_name in relation_organism_value['relationships']:
        results_holder.append(f"Relationships part: rarent "
                              f"'{relation_organism_name}' is listing "
                              f"the child as its parent")


def check_relationships(relationships):
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
                    errors.append(f"Relationships part: no entity '{relation}' "
                                  f"found")
                else:
                    current_material = convert_to_snake_case(v['material'])
                    relation_material = convert_to_snake_case(
                        relationships[relation]['material'])
                    if current_material == 'organism' and \
                            relation_material == 'organism':
                        check_parents(k, v, relation, relationships[relation],
                                      errors)
                    allowed_relationships = ALLOWED_RELATIONSHIPS[
                        current_material]
                    if relation_material not in allowed_relationships:
                        errors.append(f"Relationships part: referenced entity '"
                                      f"{relation}' does not match condition '"
                                      f"should be "
                                      f"{' or '.join(allowed_relationships)}'")
            tmp['type']['errors'].extend(errors)
        issues_to_return[name].append(tmp)
    return issues_to_return


def check_recommended_fields(record, recommended_fields):
    """
    This function will return warnings when recommended field is not present
    :param record: record to check
    :param recommended_fields: list of recommended fields to check
    :return: warning message
    """
    warnings = check_item_is_present(record, recommended_fields)
    if len(warnings) > 0:
        return f"Couldn't find these recommended fields: {', '.join(warnings)}"
    else:
        return None


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


def collect_ontology_names(json_to_parse):
    """
    This function will parse json-schema to get all ontology_names
    :param json_to_parse: json-schema to parse
    :return: dict with field name as key and ontology_name as value
    """
    ontology_names_to_return = dict()
    for field_name, field_value in json_to_parse['properties'].items():
        if field_name not in SKIP_PROPERTIES \
                and field_value['type'] == 'object':
            if check_ontology_field(field_value['properties'], 'const'):
                ontology_names_to_return[field_name] = [
                    field_value['properties']['ontology_name']['const'].lower()]
            elif check_ontology_field(field_value['properties'], 'enum'):
                ontology_names_to_return[field_name] = [
                    term.lower() for term in
                    field_value['properties']['ontology_name']['enum']]
        elif field_name not in SKIP_PROPERTIES \
                and field_value['type'] == 'array':
            if check_ontology_field(
                    field_value['items']['properties'], 'const'):
                ontology_names_to_return[field_name] = [
                    field_value['items']['properties']['ontology_name'][
                        'const'].lower()]
            elif check_ontology_field(
                    field_value['items']['properties'], 'enum'):
                ontology_names_to_return[field_name] = [
                    term.lower() for term in
                    field_value['items']['properties']['ontology_name']['enum']]
    return ontology_names_to_return


def do_additional_checks(records, url, name):
    """
    This function will return warning if recommended fields is not present in
    record
    :param records: record to check
    :param url: schema url for this record
    :param name: name of the record
    :return: warnings
    """
    issues_to_return = list()
    samples_type_json, samples_core_json = get_samples_json(url)

    # Collect list of recommended fields
    recommended_type_fields = collect_recommended_fields(samples_type_json)
    recommended_core_fields = collect_recommended_fields(samples_core_json)
    ontology_names_type = collect_ontology_names(samples_type_json)
    ontology_names_core = collect_ontology_names(samples_core_json)
    ontology_ids = collect_ids(records)

    for index, record in enumerate(records):
        # Get inner issues structure
        record_name = get_record_name(record['custom'], index, name)
        tmp = get_validation_results_structure(record_name)

        # Check that recommended fields are present
        core_warnings = check_recommended_fields(record['samples_core'],
                                                 recommended_core_fields)
        type_warnings = check_recommended_fields(record,
                                                 recommended_type_fields)
        if core_warnings is not None:
            tmp['core']['warnings'].append(core_warnings)
        if type_warnings is not None:
            tmp['type']['warnings'].append(type_warnings)

        # Check that ontology text is consistent with ontology term
        tmp['core']['warnings'].extend(
            check_ontology_text(record['samples_core'], ontology_ids,
                                ontology_names_core))
        tmp['type']['warnings'].extend(
            check_ontology_text(record, ontology_ids, ontology_names_type))

        # Check that date value is consistent with date units
        tmp['core']['warnings'].extend(
            check_date_units(record['samples_core'])
        )
        tmp['type']['warnings'].extend(
            check_date_units(record)
        )

        # TODO: Check breeds
        check_breeds()

        # Check custom fields for ontology consistence
        tmp['custom']['warnings'].extend(
            check_ontology_text(record['custom'], ontology_ids)
        )

        issues_to_return.append(tmp)
    return issues_to_return


def get_validation_results_structure(record_name):
    """
    This function will create inner validation results structure
    :param record_name: name of the record
    :return: inner validation results structure
    """
    return {
        "name": record_name,
        "core": {
            "errors": list(),
            "warnings": list()
        },
        "type": {
            "errors": list(),
            "warnings": list()
        },
        "custom": {
            "errors": list(),
            "warnings": list()
        }
    }


def get_record_name(record, index, name):
    """
    This function will return name of the current record or create it
    :param record: record to search name in
    :param index: index for new name creation
    :param name: name of the record
    :return: name of the record
    """
    if 'sample_name' not in record:
        return f"{name}_{index + 1}"
    else:
        return record['sample_name']['value']


def join_issues(to_join_to, first_record, second_record, third_record):
    """
    This function will join all issues from first and second record into one
    place
    :param to_join_to: holder that will store merged issues
    :param first_record: first record to get issues from
    :param second_record: second record to get issues from
    :param third_record: third record to get issues from
    :return: merged results
    """
    for issue_type in ['core', 'type', 'custom']:
        for issue in ['errors', 'warnings']:
            to_join_to[issue_type][issue].extend(
                first_record[issue_type][issue])
            to_join_to[issue_type][issue].extend(
                second_record[issue_type][issue])
            to_join_to[issue_type][issue].extend(
                third_record[issue_type][issue])
    return to_join_to


def collect_relationships(records, name):
    """
    This function will collect information about existing relationships and
    material types for each record
    :param records: records to parse
    :param name: name of the record, ex. 'organism'
    :return: dict with record_named as key and relationships + material as
    values
    """
    relationships = dict()
    biosample_ids = set()
    for index, record in enumerate(records):
        record_name = get_record_name(record['custom'], index, name)
        relationships.setdefault(record_name, dict())
        relationship_name = 'child_of' if name == 'organism' else 'derived_from'
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
            relationships[record_name]['organism'] = record['organism']['text']
    return relationships, biosample_ids
