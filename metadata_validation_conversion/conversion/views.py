from django.http import HttpResponse
from django.shortcuts import render
from .tasks import read_excel_file


def index(request):
    return render(request, 'conversion/index.html')


def convert_samples(request):
    res = read_excel_file.apply_async(('samples',), queue='conversion')
    return render(request, 'conversion/conversion.html', {'task_id': res.id})


def convert_experiments(request):
    read_excel_file.delay('experiments')
    return HttpResponse("This is conversion app for experiments!")
