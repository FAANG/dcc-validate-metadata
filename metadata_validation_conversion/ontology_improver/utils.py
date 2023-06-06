import requests

def hasAttribute(res, att):
    if att in res and res[att] is not None:
        if type(res[att]) is list:
            return True if len(res[att]) else False 
        return True
    return False

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

def getSynonyms(id):
    # parse ontology synonyms from EBI OLS
    res = requests.get(f"http://www.ebi.ac.uk/ols4/api/terms?short_form={id}").json()
    if '_embedded' in res:
        res = res['_embedded']['terms'][0]
        if hasAttribute(res, 'synonyms'):
            return res['synonyms']
        if 'annotation' in res and hasAttribute(res['annotation'], 'has_exact_synonym'):
            return res['annotation']['has_exact_synonym']
    return []