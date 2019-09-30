from django.http import HttpResponse
from .tasks import read_excel_file


def convert_samples(request):
    read_excel_file.delay('samples')
    return HttpResponse("This is conversion app for samples!")


def convert_experiments(request):
    read_excel_file.delay('experiments')
    return HttpResponse("This is conversion app for experiments!")
