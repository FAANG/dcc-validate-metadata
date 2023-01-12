# Create your views here.
from celery.result import AsyncResult
from django.http import JsonResponse

def get_task_details(request,task_id):
    res = AsyncResult(task_id)
    print(res.result)
    return JsonResponse({'result':res.result})