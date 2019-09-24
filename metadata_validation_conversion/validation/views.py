from django.http import HttpResponse
from metadata_validation_conversion.celery import debug_task


def index(request):
    debug_task.delay("This is validation!!!")
    return HttpResponse("This is validation app!!!")
