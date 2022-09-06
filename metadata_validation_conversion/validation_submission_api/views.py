from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .utils import convert_template, validate, domain_tasks
import json

@csrf_exempt
def validation(request, type):
    if request.method == 'POST':
        # Conversion step
        fileid = list(request.FILES.keys())[0]
        with open(f'/data/{fileid}.xlsx', 'wb+') as destination:
            for chunk in request.FILES[fileid].chunks():
                destination.write(chunk)
        conversion_results = convert_template(f'/data/{fileid}.xlsx', type)
        # Conversion error
        if conversion_results['status'] == 'Error':
            context = {
                'Error': conversion_results['error']
            }
            response = HttpResponse(
                json.dumps(context), content_type='application/json')
            response.status_code = 400
            return response
        # Validation step
        annotate_template = request.GET.get('annotate_template', 'false')
        validation_results = validate(conversion_results['result'], type, annotate_template)
        if annotate_template == 'true':
            response = HttpResponse(validation_results,
                content_type=f'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="validation_results.xlsx"'
            return response
        return JsonResponse(validation_results)
    # Incorrect method
    context = {
        'status': 403, 'reason': 'Please use POST method for validation' 
    }
    response = HttpResponse(
        json.dumps(context), content_type='application/json')
    response.status_code = 403
    return response

@csrf_exempt
def domain_actions(request, domain_action):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        result = domain_tasks(data, domain_action)
        if 'Error' in result:
            response = HttpResponse(
                json.dumps(result), content_type='application/json')
            response.status_code = 400
            return response
        return JsonResponse(result)
    # Incorrect method
    context = {
        'status': 403, 'reason': 'Please use POST method for domain actions' 
    }
    response = HttpResponse(
        json.dumps(context), content_type='application/json')
    response.status_code = 403
    return response

@csrf_exempt
def submission(request, type):
    if request.method == 'POST':
        return HttpResponse("Submission successful")
    # Incorrect method
    context = {
        'status': 403, 'reason': 'Please use POST method for submission' 
    }
    response = HttpResponse(
        json.dumps(context), content_type='application/json')
    response.status_code
    return response