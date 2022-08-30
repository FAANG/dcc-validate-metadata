import json
import requests
from celery import chain
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import read_excel_file, validate, \
    generate_hub_files, upload_files, hub_check, \
        register_trackhub, associate_specimen
import base64

@csrf_exempt
def login(request):
    if request.method != 'POST':
        return HttpResponse("This method is not allowed!\n")
    url = 'https://www.ebi.ac.uk/ena/submit/webin/auth/token'
    data = json.loads(request.body)
    password = base64.b64decode(data['password']).decode("utf-8")
    payload = {
        'username': data['username'],
        'password': password,
        'authRealms': ["ENA", "EGA"]
    }
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        token = res.text
        return JsonResponse({'token': token})
    else:
        context = {
            'status': 403, 'reason': res.text  
        }
        response = HttpResponse(
            json.dumps(context), content_type='application/json')
        response.status_code = 403
        return response

@csrf_exempt
def validation(request):
    if request.method == 'POST':
        fileid = list(request.FILES.keys())[0]
        webin_credentials = {
            'user': request.POST['user'],
            'pwd': base64.b64decode(request.POST['pwd']).decode("utf-8")
        }
        with open(f'/data/{fileid}.xlsx', 'wb+') as destination:
            for chunk in request.FILES[fileid].chunks():
                destination.write(chunk)
        # Convert Excel file to json 
        read_task = read_excel_file.s(fileid=fileid).set(queue='validation')
        # Validation level #1: validate json, generate error/ warnings list
        validate_task = validate.s(webin_credentials, fileid=fileid).set(queue='validation')
        # Generate hub files
        generate_task = generate_hub_files.s(fileid=fileid).set(queue='validation')
        # Upload track data files and hub files to file server
        upload_task = upload_files.s(webin_credentials, fileid=fileid).set(queue='validation')
        # Validation level #2: hubcheck, generate error/ warnings list
        hubcheck_task = hub_check.s(fileid=fileid).set(queue='validation')
        validation_chain = chain(read_task | validate_task \
             | generate_task | upload_task | hubcheck_task)
        res = validation_chain.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for trackhubs validation")

@csrf_exempt
def submission(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        roomid = data['fileid'] + '_submission'
        # register trackhub with the trackhub registry
        register_task = register_trackhub.s(data, roomid=roomid).set(queue='submission')
        # add track hub url to relevant specimen records
        associate_task = associate_specimen.s(roomid=roomid).set(queue='submission')
        submission_chain = chain(register_task | associate_task)
        res = submission_chain.apply_async()
        return HttpResponse(json.dumps({"id": res.id}))
    return HttpResponse("Please use POST method for registering trackhubs")