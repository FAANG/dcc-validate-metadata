from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import pprint 
pp = pprint.PrettyPrinter(indent=4)

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
            data['ontology_id'] = list(map(lambda tag: tag.split('/')[-1], response['semanticTags']))
        if 'confidence' in response:
            data['mapping_confidence'] = response['confidence']
        if 'derivedFrom' in response and 'provenance' in response['derivedFrom']:
            if 'generator' in response['derivedFrom']['provenance']:
                data['source'] = response['derivedFrom']['provenance']['generator']
        annotations.append(data)
    return annotations

@csrf_exempt
def search_terms(request):
    '''
    1. Use POST with 'terms' in body, to search for a specific set of terms, 
    returns records which are 'found' and terms which are 'not_found'
    2. Use GET to fetch all records
    '''
    if request.method == 'POST':
        terms = json.loads(request.body)['terms']
        response = {'found': [], 'not_found': []}
        for term in terms:
            # search db for term
            pass
        return JsonResponse(response)
    elif request.method == 'GET':
        response = []
        # get all records from db
        return JsonResponse(response)
    else:
        return HttpResponse("This method is not allowed!\n")

@csrf_exempt
def get_zooma_ontologies(request):
    if request.method != 'POST':
        return HttpResponse("This method is not allowed!\n")
    terms = json.loads(request.body)['terms']
    response = {}
    for term in terms:
        # data = requests.get(
        #     "http://snarf.ebi.ac.uk:8580/spot/zooma/v2/api/services/annotate?propertyValue={}&filter=preferred:[FAANG]".format(
        #      term)).json()
        data = requests.get(
            "http://www.ebi.ac.uk/spot/zooma/v2/api/services/annotate?propertyValue={}&filter=preferred:[FAANG]".format(
             term)).json()
        response[term] = parse_zooma_response(data)
    pp.pprint(response)
    return JsonResponse(response)

@csrf_exempt
def validate_terms(request):
    if request.method != 'POST':
        return HttpResponse("This method is not allowed!\n")
    data = json.loads(request.body)
    # create/update data in db
    return JsonResponse(response)