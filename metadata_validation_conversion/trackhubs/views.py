import json
from celery import chain
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import validate, upload, upload_without_val
from metadata_validation_conversion.settings import TRACKHUBS_USERNAME, TRACKHUBS_PASSWORD
import requests

@csrf_exempt
def upload_tracks(request, hub_dir, genome, sub_dir):
    if request.method == 'POST':
        firepath = f'{hub_dir}/{genome}/{sub_dir}'
        fileid_list = list(request.FILES.keys())
        res_ids = []
        for fileid in fileid_list:
            with open(f'/data/{fileid}.bb', 'wb+') as destination:
                for chunk in request.FILES[fileid].chunks():
                    destination.write(chunk)
            upload_task = upload_without_val.s(fileid, firepath,
                                str(request.FILES[fileid])).set(queue='upload')
            res = upload_task.apply_async()
            res_ids.append(res.id)
        return HttpResponse(json.dumps({"id": res_ids}))
    return HttpResponse("Please use POST method for uploading tracks")

@csrf_exempt
def upload_text_files(request, hub_dir, genome):
    if request.method == 'POST':
        fileid = list(request.FILES.keys())[0]
        filename = str(request.FILES[fileid])
        if filename == 'trackDB.txt':
            firepath = f'{hub_dir}/{genome}'
        else:
            firepath = f'{hub_dir}'
        with open(f'/data/{fileid}.bb', 'wb+') as destination:
            for chunk in request.FILES[fileid].chunks():
                destination.write(chunk)
        validate_task = validate.s(fileid, filename, genome).set(queue='upload')
        upload_task = upload.s(fileid, firepath, filename).set(queue='upload')
        upload_files_chain = chain(validate_task | upload_task)
        res = upload_files_chain.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for uploading files")

@csrf_exempt
def register_trackhub(request):
    if request.method == 'POST':
        # login and get auth token
        user = TRACKHUBS_USERNAME
        pwd = TRACKHUBS_PASSWORD
        hub_dir = json.loads(request.body)['hub_dir']
        genome_name = json.loads(request.body)['genome_name']
        genome_id = json.loads(request.body)['genome_id']
        hub_url = f"https://apifaang.org.uk/data/fire_api/trackhubregistry/{hub_dir}/hub.txt"
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
        trackdb_url = f"https://apifaang.org.uk/data/fire_api/trackhubregistry/{hub_dir}/{genome_name}/trackDB.txt"
        update_payload = { "doc": { "trackhubUrl": hub_url } }
        biosample_ids = []
        response = requests.get(trackdb_url)
        text_lines = response.text.split('\n')
        for line in text_lines:
            line = line.split(' ')
            if line[0] == 'bigDataUrl':
                biosample_ids.append(line[1].split('_')[-3])
        biosample_ids = list(set(biosample_ids))
        for id in biosample_ids:
            update_url = f"https://apifaang.org.uk/data/specimen/{id}/update"
            res = requests.put(update_url, data=json.dumps(update_payload))
        return JsonResponse("Track Hub Registered", safe=False)
    return HttpResponse("Please use POST method for registering trackhubs")

    

