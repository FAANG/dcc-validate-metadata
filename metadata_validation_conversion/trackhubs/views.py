import json
from celery import chain
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import validate, upload, upload_without_val
from metadata_validation_conversion.settings import SLACK_WEBHOOK
import requests
import os

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
def submit_trackhub(request):
    if request.method == 'POST':
        path = json.loads(request.body)['hub_path']
        hub_url = f"https://api.faang.org/trackhubs/{path}/hub.txt"
        msg_payload = {"text": f"New Track Hub Submitted at {hub_url}"}
        cmd = f"curl -X POST -H 'Content-type: application/json' --data '{json.dumps(msg_payload)}'" \
            f" {SLACK_WEBHOOK}"
        os.system(cmd)
        return JsonResponse({"message":"Track Hub Sumbitted"})
    return HttpResponse("Please use POST method for registering trackhubs")