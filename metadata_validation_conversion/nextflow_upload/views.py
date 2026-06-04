import json
from celery import chain
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from metadata_validation_conversion.helpers import is_safe_name
from .tasks import upload_to_nginx

@csrf_exempt
def upload_nextflow_file(request, dir_name):
    if request.method == 'POST':
        # dir_name (path param) and the fileids (multipart field names) are used
        # to build filesystem paths / S3 keys - restrict to the safe set to
        # prevent path traversal and injection (CWE-22 / CWE-78).
        if not is_safe_name(dir_name):
            return HttpResponse("Invalid directory name", status=400)
        fileid_list = list(request.FILES.keys())
        if not all(is_safe_name(fileid) for fileid in fileid_list):
            return HttpResponse("Invalid file identifier", status=400)
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
