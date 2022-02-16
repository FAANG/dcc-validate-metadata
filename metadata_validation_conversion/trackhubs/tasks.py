from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
import requests
import os

@app.task
def validate(fileid, filename, genome):
    send_message(submission_message="Starting to validate file",
                 room_id=fileid)
    errors = list()
    # check that genome name in genomes.txt is consistent with genome name provided
    # check that path of trackDb.txt file is correct
    if filename == 'genomes.txt':
        with open(f'/data/{fileid}.bb', 'r') as f:
            data = f.readlines()
            for line in data:
                text_line = line.split()
                if text_line[0] == 'genome' and text_line[1] != genome:
                    errors.append("Genome name in genomes.txt is not consistent with genome name provided")
                elif text_line[0] == 'trackDb' and text_line[1] != genome + '/trackDB.txt': 
                    errors.append("trackDb should have value <genome>/trackDB.txt")
            
        
    # check that links provided in trackDB.txt exist in FAANG FIRE service
    elif filename == 'trackDB.txt':
        with open(f'/data/{fileid}.bb', 'r') as f:
            data = f.readlines()
            for line in data:
                text_line = line.split()
                if len(text_line) and text_line[0] == 'bigDataUrl':
                    link = text_line[1]
                    res = requests.get(link)
                    if res.status_code != 200:
                        errors.append(f"{link} does not exist in FAANG FIRE Service")
                        break

    # check that path of genomes.txt file is correct
    elif filename == 'hub.txt':
        with open(f'/data/{fileid}.bb', 'r') as f:
            data = f.readlines()
            for line in data:
                text_line = line.split()
                if text_line[0] == 'genomesFile' and text_line[1] != 'genomes.txt':
                    errors.append("genomesFile should have value genomes.txt")

    if len(errors) != 0:
        send_message(submission_message="Validation failed",
                     errors=errors, room_id=fileid)
        return 'Error'
    else:
        return 'Success'


@app.task
def upload(validation_results, fileid, firepath, filename):
    if validation_results == 'Success':
        send_message(submission_message="Uploading file", room_id=fileid)
        filepath = f"/data/{fileid}.bb"
        url = 'http://nginx-svc:80/trackhubs_upload'
        data = {
            'path': firepath,
            'name': filename
        }
        res = requests.post(url, files={'file': open(filepath,'rb')}, data=data)
        if res.status_code != 200:
            send_message(submission_message="Upload failed, "
                                            "please contact "
                                            "faang-dcc@ebi.ac.uk",
                        room_id=fileid)
            return 'Error'
        else:
            send_message(submission_message='Success',room_id=fileid)
            # backup to s3
            cmd = f"aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 cp " \
                f"{filepath} s3://trackhubs/{firepath}/{filename}"
            os.system(cmd)
            return 'Success'
    return 'Error'

@app.task
def upload_without_val(fileid, firepath, filename):
    send_message(submission_message="Uploading file", room_id=fileid)
    filepath = f"/data/{fileid}.bb"
    url = 'http://nginx-svc:80/trackhubs_upload'
    data = {
        'path': firepath,
        'name': filename
    }
    res = requests.post(url, files={'file': open(filepath,'rb')}, data=data)
    if res.status_code != 200:
        send_message(submission_message="Upload failed, "
                                        "please contact "
                                        "faang-dcc@ebi.ac.uk",
                        room_id=fileid)
        return 'Error'
    else:
        send_message(submission_message='Success',room_id=fileid)
        # backup to s3
        cmd = f"aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 cp " \
            f"{filepath} s3://trackhubs/{firepath}/{filename}"
        os.system(cmd)
        return 'Success'
