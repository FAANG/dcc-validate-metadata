from django.http import HttpResponse
from .tasks import read_excel_file


def convert_samples(request):
    res = read_excel_file.delay('samples')
    return HttpResponse(f"Started task: {res.id}")


def convert_experiments(request):
    read_excel_file.delay('experiments')
    return HttpResponse("This is conversion app for experiments!")
