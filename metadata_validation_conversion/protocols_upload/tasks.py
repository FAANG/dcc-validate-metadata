import datetime
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from metadata_validation_conversion.constants import ORGANIZATIONS
from metadata_validation_conversion.settings import FIRE_USERNAME, FIRE_PASSWORD
from .FireAPI import FireAPI


@app.task
def validate(fileid, filename):
    send_message(submission_message="Starting to validate protocol",
                 room_id=fileid)
    errors = list()
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
        send_message(submission_message="Protocol upload failed, "
                                        "please contact faang-dcc@ebi.ac.uk",
                     errors=errors, room_id=fileid)
        return 'Error'
    else:
        return 'Success'


@app.task
def upload(validation_results, fileid, firepath):
    send_message(submission_message="Uploading protocol", room_id=fileid)
    if validation_results == 'Success':
        filepath = f"/data/{fileid}.pdf"
        fire_api_object = FireAPI(FIRE_USERNAME, FIRE_PASSWORD, filepath,
                                  firepath)
        results = fire_api_object.upload_object()
        if results == 'Error':
            send_message(submission_message="Protocol upload failed, "
                                            "please contact "
                                            "faang-dcc@ebi.ac.uk",
                         room_id=fileid)
        else:
            send_message(submission_message='Success',
                         submission_results=results,
                         room_id=fileid)
    return 'Success'
