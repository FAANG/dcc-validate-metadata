import json
from celery import chain

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .tasks import validate, upload, add_to_es


@csrf_exempt
def upload_protocol(request, protocol_type):
    if request.method == 'POST':
        fileid = list(request.FILES.keys())[0]
        filename = str(request.FILES[fileid]).split("_")
        fileserver_path = f'protocols/{protocol_type}'
        with open(f'/data/{fileid}.pdf', 'wb+') as destination:
            for chunk in request.FILES[fileid].chunks():
                destination.write(chunk)
        validate_task = validate.s(filename, fileid=fileid, protocol_type=protocol_type).set(queue='upload')
        upload_task = upload.s(fileserver_path,
                               str(request.FILES[fileid]), fileid=fileid).set(queue='upload')
        es_task = add_to_es.s(protocol_type, str(request.FILES[fileid]), fileid=fileid).set(queue='upload')
        upload_protocol_chain = chain(validate_task | upload_task | es_task)
        res = upload_protocol_chain.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for protocols upload")
