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
def submit_ontology(request):
    if request.method != 'POST':
        return HttpResponse("This method is not allowed!\n")
    terms = json.loads(request.body)['terms']
    response = {}
    for term in terms:
        data = requests.get(
            "http://snarf.ebi.ac.uk:8580/spot/zooma/v2/api/services/annotate?propertyValue={}&filter=preferred:[FAANG]".format(
             term)).json()
        response[term] = parse_zooma_response(data)
    pp.pprint(response)
    return JsonResponse(response)
