from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from ontology_improver.models import Ontologies, User
from datetime import datetime
from django.utils import timezone
from django.forms.models import model_to_dict
import base64

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
            matches = list(Ontologies.objects.filter(ontology_term__iexact=term).order_by('-created_date').values())
            if len(matches):
                response['found'] += matches
            else:
                response['not_found'].append(term)
        return JsonResponse(response)
    elif request.method == 'GET':
        size = int(request.GET.get('size', 0))
        if size:
            records = list(Ontologies.objects.all().order_by('-created_date').values()[:size])
        else:
            records = list(Ontologies.objects.all().order_by('-created_date').values())
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
def registration(request):
    if request.method != 'POST':
        return HttpResponse("This method is not allowed!\n")
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
    }
    # parse user info for creating AAP account
    request = json.loads(request.body)
    password = base64.b64decode(request['password'])
    password = password.decode("utf-8")
    post_data = {
        'username': request['username'], 
        'password': password,
        'name': request['first_name'] + ' ' + request['last_name'],
        'email': request['email'],
        'organisation': request['organisation']
    }
    res = requests.post("https://explore.api.aai.ebi.ac.uk/auth", \
        data=json.dumps(post_data), headers=headers)
    if res.status_code == 200:
        user_id = res.text
        # save user data
        User.objects.create(user_id = user_id, username = request['username'], \
            first_name = request['first_name'], \
            last_name = request['last_name'], \
            email = request['email'], institute = request['organisation'])
        return HttpResponse(user_id, status=200)
    else:
        return HttpResponse(res.text, status=res.status_code)

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
    # get user info
    user = data['user']
    user_obj = User.objects.get(username=user)
    # create/ update ontology records
    for record in ontologies:
        if record['ontology_status'] == 'Verified':
            # if status is verified and record already exists, increment verified count and add user
            try:
                obj = Ontologies.objects.get(pk=record['id'])
                obj.verified_count = obj.verified_count + 1
                obj.ontology_status = 'Verified'
                obj.save()
                obj.verified_by_users.add(user_obj)
            # if status is verified and record doesnt exist, create new record
            except (Ontologies.DoesNotExist, KeyError):
                obj = Ontologies.objects.create(
                    ontology_term=record['ontology_term'], \
                    ontology_type=record['ontology_type'], \
                    ontology_id=record['ontology_id'], \
                    ontology_support=record['ontology_support'], \
                    ontology_status=record['ontology_status'], \
                    colour_code=getColourCode(record['ontology_support'], record['ontology_status']), \
                    created_by_user = user_obj, \
                    created_date=datetime.now(tz=timezone.utc), 
                    verified_count=1)
                if 'project' in record:
                    obj.project = record['project']
                if 'tags' in record:
                    obj.tags = record['tags']
                obj.save()
                obj.verified_by_users.add(user_obj)
        # if status is not verified, always create a new record
        else:
            obj = Ontologies.objects.create(
                ontology_term=record['ontology_term'], \
                ontology_type=record['ontology_type'], \
                ontology_id=record['ontology_id'], \
                ontology_support=record['ontology_support'], \
                ontology_status=record['ontology_status'], \
                colour_code=getColourCode(record['ontology_support'], record['ontology_status']), \
                created_by_user = user_obj, \
                created_date=datetime.now(tz=timezone.utc), 
                verified_count=0) 
            if 'project' in record:
                obj.project = record['project']
            if 'tags' in record:
                obj.tags = record['tags']
            obj.save()

    return HttpResponse(status=201)

def hasAttribute(res, att):
    if att in res and res[att] is not None:
        if type(res[att]) is list:
            if len(res[att]):
                return True
            else:
                return False    
        return True
    return False

@csrf_exempt
def get_ontology_details(request, id):
    if request.method != 'GET':
        return HttpResponse("This method is not allowed!\n")
    response = {}
    # get ontology type, status etc from FAANG Ontology Database
    faang_data = model_to_dict(Ontologies.objects.get(pk=id))
    del faang_data['verified_by_users']
    response['faang_data'] = faang_data
    # parse ontology details from EBI OLS
    res = requests.get(
        "http://www.ebi.ac.uk/ols/api/terms?short_form={}".format(
            response['faang_data']['ontology_id'])).json()
    if '_embedded' in res:
        res = res['_embedded']['terms'][0]
        if hasAttribute(res, 'iri'):
            response['iri'] = res['iri'] # string
        if hasAttribute(res, 'label'):
            response['label'] = res['label'] # string
        if hasAttribute(res, 'description'):
            response['summary'] = res['description'][0] # string
        if hasAttribute(res, 'synonyms'):
            response['synonyms'] = res['synonyms'] # list
        if 'annotation' in res:
            if hasAttribute(res['annotation'], 'id'):
                response['id'] = res['annotation']['id'][0] # string 
            if hasAttribute(res['annotation'], 'has_alternative_id'):
                response['alternative_id'] = res['annotation']['has_alternative_id'] # list
            if 'summary' not in response and hasAttribute(res['annotation'], 'definition'):
                response['summary'] = res['annotation']['definition'][0] # string
            if hasAttribute(res['annotation'], 'database_cross_reference'):
                response['database_cross_reference'] = res['annotation']['database_cross_reference'] # list
            if hasAttribute(res['annotation'], 'has_related_synonym'):
                response['related_synonyms'] = res['annotation']['has_related_synonym'] # list
            if 'synonyms' not in response and hasAttribute(res['annotation'], 'has_exact_synonym'):
                response['synonyms'] = res['annotation']['has_exact_synonym'] # list
                
    return JsonResponse(response)