from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from ontology_improver.models import User
from django.conf import settings
from datetime import datetime
from django.utils import timezone
import base64
from celery import chain
from ontology_improver.utils import *
from ontology_improver.tasks import update_ontology_summary
from metadata_validation_conversion.constants import \
    BE_SVC, OLS_API, ZOOMA_SERVICE

@csrf_exempt
def get_zooma_ontologies(request):
    if request.method != 'POST':
        return HttpResponse("This method is not allowed!\n")
    terms = json.loads(request.body)['terms']
    response = {}
    for term in terms:
        data = requests.get(f"{ZOOMA_SERVICE}/annotate?propertyValue={term}&filter=preferred:[FAANG]").json()
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
    res = requests.post("https://api.aai.ebi.ac.uk/auth", \
        data=json.dumps(post_data), headers=headers)
    if res.status_code == 200:
        user_id = res.text
        # save user data
        User.objects.create(user_id = user_id, username = request['username'], \
            first_name = request['first_name'], \
            last_name = request['last_name'], \
            email = request['email'], institute = request['organisation'])
        return JsonResponse({'user_id':user_id})
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
    token = requests.get("https://api.aai.ebi.ac.uk/auth", headers=headers).text
    return JsonResponse({'token': token})

@csrf_exempt
def validate_ontology(request):
    if request.method != 'POST':
        return HttpResponse("This method is not allowed!\n")
    data = json.loads(request.body)
    ontology = data['ontology']
    status_activity = ontology['status_activity']
    status_activity.append({
        'project': data['project'],
        'status': data['status'],
        'timestamp': datetime.now(tz=timezone.utc),
        'user': data['user']
    })
    url = f"{BE_SVC}/data/ontologies/{ontology['key']}"
    res = requests.get(url)
    if res.status_code != 200 or len(json.loads(res.content)['hits']['hits']) == 0:
        return HttpResponse(status=404)
    es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection, \
                       http_auth=(settings.ES_USER, settings.ES_PASSWORD), \
                        use_ssl=True, verify_certs=True)
    if data['status'] == 'Verified':
        update_payload = {
            'status_activity': status_activity,
            'upvotes_count': ontology['upvotes_count'] + 1
        }
        es.update(index='ontologies', id=ontology['key'], body={"doc": update_payload})
    else:
        update_payload = {
            'status_activity': status_activity,
            'downvotes_count': ontology['downvotes_count'] + 1
        }
        es.update(index='ontologies', id=ontology['key'], body={"doc": update_payload})
        # create new record with suggested changes
        new_ontology = {
            'id': ontology['id'],
            'term': ontology['term'],
            'type': ontology['type'],
            'key': f"{ontology['term']}-{ontology['id']}",
            'support': '',
            'projects': data['project'] if data['project'] else [],
            'species': ontology['species'],
            'synonyms': ontology['synonyms'],
            'tags': ontology['tags'],
            'upvotes_count': 0,
            'downvotes_count': 0,
            'status_activity': [{
                'project': data['project'],
                'status': 'Awaiting Assessment',
                'timestamp': datetime.now(tz=timezone.utc),
                'user': data['user']
            }]
        }
        es.index(index='ontologies', id=new_ontology['key'], body=new_ontology)
    if 'project' in data and data['project']:
        # update summary stats - increment validated_count
        for project in data['project']:
            url = f"{BE_SVC}/data/summary_ontologies/{project}"
            project_stats = requests.get(url).json()['hits']['hits'][0]['_source']
            project_stats['activity']['validated_count'] = project_stats['activity']['validated_count'] + 1
            es.index(index='summary_ontologies', id=project, body=project_stats)
        task = update_ontology_summary.s().set(queue='submission')
        task_chain = chain(task)
        res = task_chain.apply_async()
    return HttpResponse(status=200)

@csrf_exempt
def get_ontology_details(request, id):
    if request.method != 'GET':
        return HttpResponse("This method is not allowed!\n")
    response = {}
    # get ontology type, status etc from FAANG Ontology Database
    url = f"{BE_SVC}/data/ontologies/{id}"
    res = requests.get(url)
    if res.status_code != 200 or len(json.loads(res.content)['hits']['hits']) == 0:
        return HttpResponse(status=404)
    faang_data = json.loads(res.content)['hits']['hits'][0]['_source']
    response['faang_data'] = faang_data
    # parse ontology details from EBI OLS
    res = requests.get(f"{OLS_API}/terms?short_form={response['faang_data']['id']}").json()
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

@csrf_exempt
def ontology_updates(request):
    if request.method != 'POST':
        return HttpResponse("This method is not allowed!\n")
    data = json.loads(request.body)
    ontologies = data['ontologies']
    # get user info
    user = data['user']
    es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection, \
                       http_auth=(settings.ES_USER, settings.ES_PASSWORD), \
                        use_ssl=True, verify_certs=True)
    for ontology in ontologies:
        url = f"{BE_SVC}/data/ontologies/{ontology['key']}"
        res = requests.get(url)
        # create new ontology if ontology does not exist
        if res.status_code != 200 or len(json.loads(res.content)['hits']['hits']) == 0:
            new_ontology = {
                'id': ontology['id'],
                'term': ontology['term'],
                'type': ontology['type'],
                'key': f"{ontology['term']}-{ontology['id']}",
                'support': ontology['support'] if ontology['support'] else '',
                'projects': ontology['projects'] if ontology['projects'] else [],
                'species': ontology['species'] if ontology['species'] else [],
                'synonyms': ontology['synonyms'] if ontology['synonyms'] else getSynonyms(ontology['id']),
                'tags': ontology['tags'] if ontology['tags'] else [],
                'upvotes_count': 0,
                'downvotes_count': 0,
                'status_activity': [{
                    'project': ontology['projects'],
                    'status': 'Awaiting Assessment',
                    'timestamp': datetime.now(tz=timezone.utc),
                    'user': user
                }]
            }
            es.index(index='ontologies', id=new_ontology['key'], body=new_ontology)
        # edit ontology if it already exists
        else:
            existing_ontology = json.loads(res.content)['hits']['hits'][0]['_source']
            update_payload = {
                'type': ontology['type'],
                'synonyms': ontology['synonyms'],
                'projects': ontology['projects'],
                'species': ontology['species'],
                'tags': ontology['tags']
            }
            es.update(index='ontologies', id=existing_ontology['key'], body={"doc": update_payload})
    # update summary statistics
    task = update_ontology_summary.s().set(queue='submission')
    task_chain = chain(task)
    res = task_chain.apply_async()
    return HttpResponse(status=201)
