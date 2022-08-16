from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

@csrf_exempt
def validation(request):
    return HttpResponse("Validation successful")

@csrf_exempt
def submission(request):
    return HttpResponse("Submission successful")