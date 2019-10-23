from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .tasks import read_excel_file


def index(request):
    return render(request, 'conversion/index.html')


@csrf_exempt
def convert_samples(request):
    if request.method == 'POST':
        with open('file.xlsx', 'wb+') as destination:
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)
        res = read_excel_file.apply_async(('samples', 'file.xlsx'),
                                          queue='conversion')
        return HttpResponse(f"Conversion started: {res.id}")
    # TODO convert it to error response
    return HttpResponse("Please use POST method for conversion!")


@csrf_exempt
def convert_experiments(request):
    read_excel_file.delay('experiments')
    return HttpResponse("This is conversion app for experiments!")