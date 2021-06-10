from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from ontology_improver.models import Ontologies
from datetime import datetime
from django.utils import timezone

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
            data['ontology_id'] = ','.join(response['semanticTags'])
        if 'confidence' in response:
            data['mapping_confidence'] = response['confidence']
        if 'derivedFrom' in response and 'provenance' in response['derivedFrom']:
            if 'generator' in response['derivedFrom']['provenance']:
                data['source'] = response['derivedFrom']['provenance']['generator']
        annotations.append(data)
    return annotations

def getColourCode(ontology_support, ontology_status):
    if ontology_status == 'Verified':
        if ontology_support == 'https://www.ebi.ac.uk/vg/faang':
            return 'green'
        else:
            return 'yellow'
    elif ontology_status == 'Awaiting Assessment':
        return 'blue'
    elif ontology_status == 'Needs Improvement':
        return 'yellow'
    else:
        return 'red'

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
            matches = list(Ontologies.objects.filter(ontology_term__iexact=term).values())
            if len(matches):
                response['found'].append(matches[0])
            else:
                response['not_found'].append(term)
        return JsonResponse(response)
    elif request.method == 'GET':
        size = int(request.GET.get('size', 0))
        if size:
            records = list(Ontologies.objects.all().values()[:size])
        else:
            records = list(Ontologies.objects.all().values())
        response = {
            'ontologies': records
        }
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
        data = requests.get(
            "http://www.ebi.ac.uk/spot/zooma/v2/api/services/annotate?propertyValue={}&filter=preferred:[FAANG]".format(
             term)).json()
        response[term] = parse_zooma_response(data)
    return JsonResponse(response)

@csrf_exempt
def authentication(request):
    if request.method != 'POST':
        return HttpResponse("This method is not allowed!\n")
    headers = {
        'Accept': 'text/plain',
        'Authorization': json.loads(request.body)['auth']
    }
    token = requests.get("https://explore.api.aai.ebi.ac.uk/auth", headers=headers).text
    return JsonResponse({'token': token})

@csrf_exempt
def validate_terms(request):
    if request.method != 'POST':
        return HttpResponse("This method is not allowed!\n")
    data = json.loads(request.body)
    ontologies = data['ontologies']
    user = data['user']
    for record in ontologies:
        matches = list(Ontologies.objects.filter(ontology_term__iexact=record['ontology_term']).values())
        if len(matches):
            # update record if already exists
            ontology = Ontologies.objects.get(id=matches[0]['id'])
            ontology.ontology_term = record['ontology_term']
            ontology.ontology_type = record['ontology_type']
            ontology.ontology_id = record['ontology_id']
            ontology.ontology_support = record['ontology_support']
            ontology.ontology_status = record['ontology_status']
            ontology.users = ontology.users + ',' + user
            ontology.colour_code = getColourCode(record['ontology_support'], record['ontology_status'])
            ontology.last_updated = datetime.now(tz=timezone.utc)
            if record['ontology_status'] == 'Verified':
                ontology.verified_count  = ontology.verified_count + 1
            ontology.save()
        else:
            # create record if not found
            verified_num  = 1 if record['ontology_status'] == 'Verified' else 0
            Ontologies(ontology_term=record['ontology_term'], ontology_type=record['ontology_type'], \
                ontology_id=record['ontology_id'], ontology_support=record['ontology_support'], \
                ontology_status=record['ontology_status'], users=user, \
                colour_code=getColourCode(record['ontology_support'], record['ontology_status']), \
                last_updated=datetime.now(tz=timezone.utc), verified_count=verified_num).save()   
        pass
    return HttpResponse(status=201)