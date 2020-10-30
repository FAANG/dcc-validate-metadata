import datetime

from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from metadata_validation_conversion.helpers import send_message
from metadata_validation_conversion.constants import ORGANIZATIONS
from .tasks import upload


@csrf_exempt
def upload_protocol(request, task_id):
    if request.method == 'POST':
        errors = list()
        fileid = list(request.FILES.keys())[0]
        send_message(submission_message="Starting to validate protocol",
                     room_id=fileid)
        filename = str(request.FILES[fileid]).split("_")
        if filename[0] not in ORGANIZATIONS:
            errors.append(f"Your organization {filename[0]} was not found")
        if filename[1] != 'SOP':
            errors.append("Please add SOP tag in your protocol name")
        protocol_date = filename[-1].split('.pdf')[0]
        try:
            datetime.datetime.strptime(protocol_date, '%Y%m%d')
        except ValueError:
            errors.append("Incorrect date format, should be YYYYMMDD")
        if len(errors) != 0:
            send_message(submission_message="Protocol upload failed",
                         errors=errors, room_id=fileid)
        else:
            send_message(submission_message='Success',
                         submission_results=f"https://data.faang.org/api/"
                                            f"fire_api/samples/"
                                            f"{str(request.FILES[fileid])}",
                         room_id=fileid)
        return HttpResponse("Success")
    return HttpResponse("Please use POST method for protocols upload")
