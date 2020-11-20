import json
from celery import chain

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .tasks import validate, upload


@csrf_exempt
def upload_protocol(request, protocol_type):
    if request.method == 'POST':
        fileid = list(request.FILES.keys())[0]
        filename = str(request.FILES[fileid]).split("_")
        firepath = protocol_type
        with open(f'/data/{fileid}.pdf', 'wb+') as destination:
            for chunk in request.FILES[fileid].chunks():
                destination.write(chunk)
        validate_task = validate.s(fileid, filename).set(queue='upload')
        upload_task = upload.s(fileid, firepath,
                               str(request.FILES[fileid])).set(queue='upload')
        upload_protocol_chain = chain(validate_task | upload_task)
        res = upload_protocol_chain.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for protocols upload")
