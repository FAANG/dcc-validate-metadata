from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from metadata_validation_conversion.helpers import send_message
from .tasks import read_excel_file


def index(request):
    return render(request, 'conversion/index.html')


@csrf_exempt
def convert_samples(request):
    send_message(conversion_status="Waiting")
    if request.method == 'POST':
        with open('samples.xlsx', 'wb+') as destination:
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
        res = read_excel_file.apply_async(('samples', 'samples.xlsx'),
                                          queue='conversion')
        return HttpResponse(res.id)
    return HttpResponse("Please use POST method for conversion!")


@csrf_exempt
def convert_experiments(request):
    send_message(conversion_status="Waiting")
    if request.method == 'POST':
        with open('experiments.xlsx', 'wb+') as destination:
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
        res = read_excel_file.apply_async(('experiments', 'experiments.xlsx'),
                                          queue='conversion')
        return HttpResponse(res.id)
    return HttpResponse("Please use POST method for conversion")


@csrf_exempt
def convert_analyses(request):
    send_message(conversion_status="Waiting")
    if request.method == 'POST':
        with open('analyses.xlsx', 'wb+') as destination:
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
        res = read_excel_file.apply_async(('analyses', 'analyses.xlsx'),
                                          queue='conversion')
        return HttpResponse(res.id)
    return HttpResponse("Please use POST method for conversion")
