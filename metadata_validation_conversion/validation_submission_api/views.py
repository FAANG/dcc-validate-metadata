from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .utils import convert_template
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
            response.status_code = 404
            return response
        # TODO: Validation step
        return JsonResponse(conversion_results)
    # Incorrect method
    context = {
        'status': 403, 'reason': 'Please use POST method for validation' 
    }
    response = HttpResponse(
        json.dumps(context), content_type='application/json')
    response.status_code = 403
    return response

@csrf_exempt
def submission(request):
    return HttpResponse("Submission successful")