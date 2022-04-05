import json
from celery import chain
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import upload_to_nginx

@csrf_exempt
def upload_nextflow_file(request, dir_name):
    if request.method == 'POST':
        fileid_list = list(request.FILES.keys())
        res_ids = []
        for fileid in fileid_list:
            with open(f'/data/{fileid}', 'wb+') as destination:
                for chunk in request.FILES[fileid].chunks():
                    destination.write(chunk)
            upload_task = upload_to_nginx.s(fileid, dir_name, str(request.FILES[fileid])).set(queue='upload')
            res = upload_task.apply_async()
            res_ids.append(res.id)
        return HttpResponse(json.dumps({"id": res_ids}))
    return HttpResponse("Please use POST method for uploading NextFlow config files")
