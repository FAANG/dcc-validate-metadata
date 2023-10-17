import requests
from urllib.error import HTTPError
from metadata_validation_conversion.constants import RULESET_URL


def parse_zooma_response(response_list):
    annotations = []
    for response in response_list:
        data = {}
        if 'annotatedProperty' in response:
            if 'propertyType' in response['annotatedProperty']:
                data['term_type'] = response['annotatedProperty']['propertyType']
            if 'propertyValue' in response['annotatedProperty']:
                data['ontology_label'] = response['annotatedProperty']['propertyValue']
        if 'semanticTags' in response:
            data['ontology_id'] = ','.join(list(map(lambda tag: tag.split('/')[-1], response['semanticTags'])))
        if 'confidence' in response:
            data['mapping_confidence'] = response['confidence']
        if 'derivedFrom' in response and 'provenance' in response['derivedFrom']:
            if 'generator' in response['derivedFrom']['provenance']:
                data['source'] = response['derivedFrom']['provenance']['generator']
        annotations.append(data)
    return annotations


def get_ontology_names():
    try:
        ontology_classes_set = set()
        # standard
        url = f'{RULESET_URL}/core/samples/faang_samples_core.metadata_rules.json'
        data = requests.get(url).json()
        terms_list = data['properties']['material']['properties']['term']['enum']
        ontology_classes_set.update(list(map(lambda term: term.split(':')[0], terms_list)))

        # organism
        url = f'{RULESET_URL}/type/samples/faang_samples_organism.metadata_rules.json'
        ontology_classes_set.update(get_ontologies_list(url))

        # organoid
        url = f'{RULESET_URL}/type/samples/faang_samples_organoid.metadata_rules.json'
        ontology_classes_set.update(get_ontologies_list(url))

        # specimen_standard_rule
        url = f'{RULESET_URL}/type/samples/faang_samples_specimen.metadata_rules.json'
        ontology_classes_set.update(get_ontologies_list(url))

        # specimen_teleostei_embryo
        url = f'{RULESET_URL}/module/samples/faang_samples_specimen_teleost_embryo.metadata_rules.json'
        ontology_classes_set.update(get_ontologies_list(url))

        # specimen_teleostei_post
        url = f'{RULESET_URL}/module/samples/faang_samples_specimen_teleost_post-hatching.metadata_rules.json'
        ontology_classes_set.update(get_ontologies_list(url))

        # single_cell_specimen
        url = f'{RULESET_URL}/type/samples/faang_samples_single_cell_specimen.metadata_rules.json'
        ontology_classes_set.update(get_ontologies_list(url))

        # samples_pool_of_specimens
        url = f'{RULESET_URL}/type/samples/faang_samples_pool_of_specimens.metadata_rules.json'
        ontology_classes_set.update(get_ontologies_list(url))

        # samples_purified_cells
        url = f'{RULESET_URL}/type/samples/faang_samples_purified_cells.metadata_rules.json'
        ontology_classes_set.update(get_ontologies_list(url))

        # samples_cell_culture
        url = f'{RULESET_URL}/type/samples/faang_samples_cell_culture.metadata_rules.json'
        ontology_classes_set.update(get_ontologies_list(url))

        # samples_cell_line
        url = f'{RULESET_URL}/type/samples/faang_samples_cell_line.metadata_rules.json'
        ontology_classes_set.update(get_ontologies_list(url))

        faang_ontology_classes = list(
            filter(lambda ontology_name: ontology_name != 'restricted access' and ontology_name is not None,
                   ontology_classes_set))

        ontologies_str = ','.join(faang_ontology_classes)
        return ontologies_str

    except HTTPError as err:
        print(err.reason)


def gen_dict_extract(key, var):
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result


def get_ontologies_list(url):
    main_list = []
    data = requests.get(url).json()['properties']
    for x in gen_dict_extract("classes", data):
        main_list.extend(list(map(lambda term: term.split(':')[0] if ':' in term else None, x)))
    return main_list
