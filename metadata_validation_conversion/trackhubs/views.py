import json
from celery import chain
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import validate, upload, upload_without_val

@csrf_exempt
def upload_tracks(request, genome_id, directory):
    if request.method == 'POST':
        fileid = list(request.FILES.keys())[0]
        firepath = genome_id + '/' + directory
        with open(f'/data/{fileid}.bb', 'wb+') as destination:
            for chunk in request.FILES[fileid].chunks():
                destination.write(chunk)
        upload_task = upload_without_val.s(fileid, firepath,
                               str(request.FILES[fileid])).set(queue='upload')
        res = upload_task.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for uploading tracks")

@csrf_exempt
def upload_text_files(request, genome_id):
    if request.method == 'POST':
        fileid = list(request.FILES.keys())[0]
        filename = str(request.FILES[fileid])
        firepath = genome_id
        with open(f'/data/{fileid}.bb', 'wb+') as destination:
            for chunk in request.FILES[fileid].chunks():
                destination.write(chunk)
        validate_task = validate.s(fileid, filename, genome_id).set(queue='upload')
        upload_task = upload.s(fileid, firepath, filename).set(queue='upload')
        upload_files_chain = chain(validate_task | upload_task)
        res = upload_files_chain.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for uploading files")
