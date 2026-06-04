import json
from celery import chain

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from metadata_validation_conversion.helpers import is_safe_name
from .tasks import validate, upload, add_to_es


@csrf_exempt
def upload_protocol(request, protocol_type):
    if request.method == 'POST':
        # protocol_type (path param) and fileid (multipart field name) end up in
        # filesystem paths and S3 keys - restrict to the safe set (CWE-22/78).
        if not is_safe_name(protocol_type):
            return HttpResponse("Invalid protocol type", status=400)
        fileid = list(request.FILES.keys())[0]
        if not is_safe_name(fileid):
            return HttpResponse("Invalid file identifier", status=400)
        filename = str(request.FILES[fileid]).split("_")
        fileserver_path = f'protocols/{protocol_type}'
        with open(f'/data/{fileid}.pdf', 'wb+') as destination:
            for chunk in request.FILES[fileid].chunks():
                destination.write(chunk)
        validate_task = validate.s(filename, fileid=fileid).set(queue='upload')
        upload_task = upload.s(fileserver_path,
                               str(request.FILES[fileid]), fileid=fileid).set(queue='upload')
        es_task = add_to_es.s(protocol_type, str(request.FILES[fileid]), fileid=fileid).set(queue='upload')
        upload_protocol_chain = chain(validate_task | upload_task | es_task)
        res = upload_protocol_chain.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for protocols upload")
