from django.http import HttpResponse
from metadata_validation_conversion.celery import debug_task


def index(request):
    debug_task.delay("This is conversion!!!")
    return HttpResponse("This is conversion app!!!")
