from django.http import HttpResponse
from metadata_validation_conversion.celery import debug_task
from .tasks import read_excel_file


def index(request):
    read_excel_file.delay()
    return HttpResponse("This is conversion app!!!")
