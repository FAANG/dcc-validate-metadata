from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from metadata_validation_conversion.settings import FIRE_USERNAME, FIRE_PASSWORD
from .FireAPI import FireAPI


@app.task
def validate(fileid, filename):
    send_message(submission_message="Starting to validate file",
                 room_id=fileid)
    errors = list()
    if '.txt' not in filename[-1]:
        errors.append("Please use txt format only")
    # check that genome name in genomes.txt is consistent with genome name provided
    # check that links provided in trackDB.txt exist in FAANG FIRE service
    if len(errors) != 0:
        send_message(submission_message="Validation failed",
                     errors=errors, room_id=fileid)
        return 'Error'
    else:
        return 'Success'


@app.task
def upload(validation_results, fileid, firepath, filename):
    send_message(submission_message="Uploading file", room_id=fileid)
    if validation_results == 'Success':
        filepath = f"/data/{fileid}.bb"
        fire_api_object = FireAPI(FIRE_USERNAME, FIRE_PASSWORD, filepath,
                                  firepath, filename)
        results = fire_api_object.upload_object()
        if results == 'Error':
            send_message(submission_message="Upload failed, "
                                            "please contact "
                                            "faang-dcc@ebi.ac.uk",
                         room_id=fileid)
        else:
            send_message(submission_message='Success',
                         submission_results=results,
                         room_id=fileid)
    return 'Success'

@app.task
def upload_without_val(fileid, firepath, filename):
    send_message(submission_message="Uploading file", room_id=fileid)
    filepath = f"/data/{fileid}.bb"
    fire_api_object = FireAPI(FIRE_USERNAME, FIRE_PASSWORD, filepath,
                                firepath, filename)
    results = fire_api_object.upload_object()
    send_message(submission_message=results, room_id=fileid)
    if results == 'Error':
        send_message(submission_message="Upload failed, "
                                        "please contact "
                                        "faang-dcc@ebi.ac.uk",
                        room_id=fileid)
    else:
        send_message(submission_message='Success',
                        submission_results=results,
                        room_id=fileid)
    return 'Success'
