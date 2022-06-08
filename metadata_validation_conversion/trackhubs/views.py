import json
from celery import chain
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import read_excel_file, validate, \
    generate_hub_files, upload_files, hub_check
from metadata_validation_conversion.settings import \
    TRACKHUBS_USERNAME, TRACKHUBS_PASSWORD
import requests
import os

@csrf_exempt
def validation(request):
    if request.method == 'POST':
        fileid = list(request.FILES.keys())[0]
        with open(f'/data/{fileid}.xlsx', 'wb+') as destination:
            for chunk in request.FILES[fileid].chunks():
                destination.write(chunk)
        # Convert Excel file to json 
        read_task = read_excel_file.s(fileid).set(queue='upload')
        # Validation level #1: validate json, generate error/ warnings list
        validate_task = validate.s(fileid).set(queue='upload')
        # Generate hub files
        generate_task = generate_hub_files.s(fileid).set(queue='upload')
        # Upload track data files and hub files to file server
        upload_task = upload_files.s(fileid).set(queue='upload')
        # Validation level #2: hubcheck, generate error/ warnings list
        hubcheck_task = hub_check.s(fileid).set(queue='upload')
        validation_chain = chain(read_task | validate_task \
             | generate_task | upload_task | hubcheck_task)
        res = validation_chain.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for trackhubs validation")

@csrf_exempt
def submission(request):
    if request.method == 'POST':
        # login and get auth token
        user = TRACKHUBS_USERNAME
        pwd = TRACKHUBS_PASSWORD
        hub_dir = json.loads(request.body)['hub_dir']
        genome_name = json.loads(request.body)['genome_name']
        genome_id = json.loads(request.body)['genome_id']
        hub_url = f"https://api.faang.org/files/trackhubs/{hub_dir}/hub.txt"
        r = requests.get('https://www.trackhubregistry.org/api/login', auth=(user, pwd), verify=True)
        if not r.ok:
            return HttpResponse(f"Authentication failed: {r.text}", status=r.status_code)
        auth_token = r.json()[u'auth_token']

        # register tracks with trackhubs registry
        headers = { 'user': user, 'auth_token': auth_token }
        payload = { 'url': hub_url, 'assemblies': { genome_name: genome_id } }
        r = requests.post('https://www.trackhubregistry.org/api/trackhub', headers=headers, json=payload, verify=True)
        if not r.ok:
            return HttpResponse(f"Registration failed: {r.text}", status=r.status_code)

        # add track hub url to relevant records
        trackdb_url = f"http://nginx-svc:80/files/trackhubs/{hub_dir}/{genome_name}/trackDb.txt"
        update_payload = { "doc": { "trackhubUrl": hub_url } }
        biosample_ids = []
        response = requests.get(trackdb_url)
        text_lines = response.text.split('\n')
        for line in text_lines:
            line = line.split(' ')
            if line[0] == 'bigDataUrl':
                biosample_ids.append(line[1].split('_')[-1].split('.')[0])
        biosample_ids = list(set(biosample_ids))
        for id in biosample_ids:
            update_url = f"http://daphne-svc:8000/data/specimen/{id}/update"
            res = requests.put(update_url, data=json.dumps(update_payload))
        return JsonResponse("Track Hub Registered", safe=False)
    return HttpResponse("Please use POST method for registering trackhubs")