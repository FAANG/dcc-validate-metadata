from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from metadata_validation_conversion.helpers import send_message
from .tasks import read_excel_file


def index(request):
    return render(request, 'conversion/index.html')


@csrf_exempt
def convert_template(request, task_id):
    if request.method == 'POST':
        fileid = list(request.FILES.keys())[0]
        send_message(room_id=fileid, conversion_status="Waiting")
        with open(f'{fileid}.xlsx', 'wb+') as destination:
            for chunk in request.FILES[fileid].chunks():
                destination.write(chunk)
        res = read_excel_file.apply_async((fileid, task_id, f'{fileid}.xlsx'),
                                          queue='conversion')
        res.get()
        return HttpResponse(res.id)
    return HttpResponse("Please use POST method for conversion!")
