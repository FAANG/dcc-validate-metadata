from abc import ABC

from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from collections import OrderedDict
from metadata_validation_conversion.settings import \
    MINIO_ACCESS_KEY, MINIO_SECRET_KEY, \
    TRACKHUBS_USERNAME, TRACKHUBS_PASSWORD
import requests
import xlrd
import json
import os
from celery import Task


class LogErrorsTask(Task, ABC):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if 'fileid' in kwargs:
            send_message(room_id=kwargs['fileid'], submission_message='Error with trackhub upload',
                         errors=f'Error: {exc}')
        if 'roomid' in kwargs:
            send_message(room_id=kwargs['roomid'], submission_message='Error with trackhub upload',
                         errors=f'Error: {exc}')


@app.task(base=LogErrorsTask)
def read_excel_file(fileid):
    send_message(room_id=fileid, submission_message="Converting template")
    wb = xlrd.open_workbook(f'/data/{fileid}.xlsx')
    data_dict = dict()
    error_flag = False
    try:
        for sh in wb.sheets():
            data_dict[sh.name] = []
            for rownum in range(1, sh.nrows):
                data = OrderedDict()
                row_values = sh.row_values(rownum)
                if sh.name == 'Hub Data':
                    data['Name'] = row_values[0]
                    data['Short Label'] = row_values[1]
                    data['Long Label'] = row_values[2]
                    data['Email'] = row_values[3]
                    data['Description File Path'] = row_values[4]  # optional field
                elif sh.name == 'Genome Data':
                    data['Assembly Accession'] = row_values[0]
                    data['Organism'] = row_values[1]  # optional field
                    data['Description'] = row_values[2]  # optional field
                elif sh.name == 'Tracks Data':
                    data['Track Name'] = row_values[0]
                    data['File Path'] = row_values[1]
                    data['File Type'] = row_values[2]
                    data['Short Label'] = row_values[3]
                    data['Long Label'] = row_values[4]
                    data['Related Specimen ID'] = row_values[5]
                    data['Subdirectory'] = row_values[6]
                data_dict[sh.name].append(data)
        send_message(room_id=fileid, submission_message="Template converted successfully")
    except:
        send_message(room_id=fileid, submission_message="Error while converting template")
        error_flag = True
    finally:
        return {'error_flag': error_flag, 'data': data_dict}


@app.task(base=LogErrorsTask)
def validate(result, fileid):
    error_flag = result['error_flag']
    if not error_flag:
        send_message(submission_message="Starting to validate file",
                     room_id=fileid)
        error_dict = {}
        data_dict = result['data']
        # set alias for minio
        cmd = f"./mc alias set minio-trackhubs http://minio-svc-trackhubs.default:80 " \
              f"{MINIO_ACCESS_KEY} {MINIO_SECRET_KEY}"
        os.system(cmd)
        for key in data_dict:
            error_dict[key] = []
            for row_index in range(len(data_dict[key])):
                errors = {}
                if key == 'Hub Data':
                    for row_prop in data_dict[key][row_index]:
                        # check that all required fields are present
                        if not data_dict[key][row_index][row_prop] and row_prop != 'Description File Path':
                            error_flag = True
                            errors[row_prop] = f'Required field: {row_prop} cannot be empty'
                elif key == 'Genome Data':
                    assembly_name = ''
                    for row_prop in data_dict[key][row_index]:
                        # check that all required fields are present
                        if not data_dict[key][row_index][
                            row_prop] and row_prop != 'Organism' and row_prop != 'Description':
                            error_flag = True
                            errors[row_prop] = f'Required field: {row_prop} cannot be empty'
                        # check "Assembly Accession" is valid
                        if row_prop == 'Assembly Accession' and row_prop not in errors:
                            url = f"https://rest.ensembl.org/info/genomes/assembly/" \
                                  f"{data_dict[key][row_index][row_prop]}?content-type=application/json"
                            res = requests.get(url)
                            if res.status_code == 200:
                                res_json = json.loads(res.content)
                                assembly_name = res_json['assembly_name']
                            else:
                                error_flag = True
                                errors[row_prop] = f'Assembly Accession {data_dict[key][row_index][row_prop]}' \
                                                   f' is not a valid GCA accession'
                    if len(assembly_name):
                        data_dict[key][row_index]['Assembly Name'] = assembly_name
                elif key == 'Tracks Data':
                    for row_prop in data_dict[key][row_index]:
                        # check that all required fields are present
                        if not data_dict[key][row_index][row_prop]:
                            error_flag = True
                            errors[row_prop] = f'Required field: {row_prop} cannot be empty'
                        # check that "File Path" exists in MinIO server
                        if row_prop == 'File Path' and row_prop not in errors:
                            cmd = f"./mc find minio-trackhubs/{data_dict[key][row_index][row_prop]}"
                            c = os.system(cmd)
                            if c != 0:
                                error_flag = True
                                errors[row_prop] = f'File {data_dict[key][row_index][row_prop]} not found'
                        # check that "File Type" is valid
                        elif row_prop == 'File Type' and row_prop not in errors:
                            valid_types = ['bigWig', 'bigBed', 'bigBarChart', \
                                           'bigGenePred', 'bigInteract', 'bigNarrowPeak', \
                                           'bigChain', 'bigPsl', 'bigMaf', 'hic', 'bam', \
                                           'halSnake', 'vcfTabix']
                            if data_dict[key][row_index][row_prop] not in valid_types:
                                error_flag = True
                                errors[row_prop] = f'File type {data_dict[key][row_index][row_prop]} is not valid. ' \
                                                   f'Please use one of the following types: {", ".join(valid_types)}'
                        # check that "Related Specimen ID" is a valid BioSamples ID
                        elif row_prop == 'Related Specimen ID' and row_prop not in errors:
                            url = f'http://daphne-svc:8000/data/specimen/{data_dict[key][row_index][row_prop]}'
                            res = requests.get(url)
                            if res.status_code != 200 or len(json.loads(res.content)['hits']['hits']) == 0:
                                error_flag = True
                                errors[
                                    row_prop] = f'{data_dict[key][row_index][row_prop]} is not a valid FAANG Specimen'
                error_dict[key].append(errors)
        if error_flag:
            data_dict['errors'] = error_dict
            send_message(room_id=fileid, submission_message="Error: Template validation failed",
                         validation_results=data_dict)
            print(error_dict)
            return {'error_flag': error_flag, 'data': error_dict}
        else:
            send_message(room_id=fileid, submission_message="Template validation successful")
            return {'error_flag': error_flag, 'data': data_dict}
    return {'error_flag': error_flag, 'data': data_dict}


@app.task(base=LogErrorsTask)
def generate_hub_files(result, fileid):
    error_flag = result['error_flag']
    res_dict = result['data']
    if not error_flag:
        try:
            send_message(room_id=fileid, submission_message="Generating Hub files")
            hub = res_dict['Hub Data'][0]['Name']
            genome = res_dict['Genome Data'][0]['Assembly Name']
            file_server = 'https://api.faang.org/files/trackhubs'
            cmd = f'mkdir /data/{hub}'
            os.system(cmd)
            # generate hub.txt
            with open(f'/data/{hub}/hub.txt', 'w') as f:
                f.write(f"hub {res_dict['Hub Data'][0]['Name']}\n")
                f.write(f"shortLabel {res_dict['Hub Data'][0]['Short Label']}\n")
                f.write(f"longLabel {res_dict['Hub Data'][0]['Long Label']}\n")
                f.write("genomesFile genomes.txt\n")
                f.write(f"email {res_dict['Hub Data'][0]['Email']}\n")
                if res_dict['Hub Data'][0]['Description File Path']:
                    f.write(f"descriptionUrl {res_dict['Hub Data'][0]['Description File Path']}\n")
            # generate genomes.txt
            with open(f'/data/{hub}/genomes.txt', 'w') as f:
                f.write(f"genome {res_dict['Genome Data'][0]['Assembly Name']}\n")
                f.write(f"trackDb {res_dict['Genome Data'][0]['Assembly Name']}/trackDb.txt\n")
                if res_dict['Genome Data'][0]['Description']:
                    f.write(f"description {res_dict['Genome Data'][0]['Description']}\n")
                if res_dict['Genome Data'][0]['Organism']:
                    f.write(f"organism {res_dict['Genome Data'][0]['Organism']}\n")
            # generate trackDb.txt
            with open(f'/data/{hub}/trackDb.txt', 'w') as f:
                for row in res_dict['Tracks Data']:
                    file_name = row['File Path'].split('/')[-1]
                    file_name = f"{file_name.split('.')[0]}_{row['Related Specimen ID']}.{file_name.split('.')[1]}"
                    track_url = f"{file_server}/{hub}/{genome}/{row['Subdirectory']}/{file_name}"
                    f.write(f"track {row['Track Name']}\n")
                    f.write(f"bigDataUrl {track_url}\n")
                    f.write(f"shortLabel {row['Short Label']}\n")
                    f.write(f"longLabel {row['Long Label']}\n")
                    f.write(f"type {row['File Type']}\n\n")
            send_message(room_id=fileid,
                         submission_message="Track Hub files generated")
        except:
            send_message(room_id=fileid,
                         submission_message="Error generating Track Hub files, please contact faang-dcc@ebi.ac.uk")
        finally:
            return {'error_flag': error_flag, 'data': res_dict}
    return {'error_flag': error_flag, 'data': res_dict}


@app.task(base=LogErrorsTask)
def upload_files(result, fileid):
    error_flag = result['error_flag']
    res_dict = result['data']
    if not error_flag:
        send_message(room_id=fileid, submission_message="Setting up Track Hub")
        hub = res_dict['Hub Data'][0]['Name']
        genome = res_dict['Genome Data'][0]['Assembly Name']
        url = 'http://nginx-svc:80/files_upload'
        files = ['hub.txt', 'genomes.txt', 'trackDb.txt']
        # upload generated hub files to trackhubs local storage
        for file in files:
            filepath = f"/data/{hub}/{file}"
            if file == 'trackDb.txt':
                server_path = f"trackhubs/{hub}/{genome}"
            else:
                server_path = f"trackhubs/{hub}"
            data = {
                'path': server_path,
                'name': file
            }
            res = requests.post(url, files={'file': open(filepath, 'rb')}, data=data)
            if res.status_code != 200:
                error_flag = True
            else:
                # backup to s3
                cmd = f"aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 cp " \
                      f"{filepath} s3://{data['path']}/{data['name']}"
                os.system(cmd)
        # copy files from minio and upload to trackhubs local storage
        for track in res_dict['Tracks Data']:
            file = track['File Path'].split('/')[-1]
            filepath = f'/data/{hub}/{file}'
            cmd = f"./mc cp minio-trackhubs/{track['File Path']} {filepath}"
            os.system(cmd)
            data = {
                'path': f"trackhubs/{hub}/{genome}/{track['Subdirectory']}",
                'name': f"{file.split('.')[0]}_{track['Related Specimen ID']}.{file.split('.')[1]}"
            }
            res = requests.post(url, files={'file': open(filepath, 'rb')}, data=data)
            if res.status_code != 200:
                error_flag = True
            else:
                # backup to s3
                cmd = f"aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 cp " \
                      f"{filepath} s3://{data['path']}/{data['name']}"
                os.system(cmd)
        if not error_flag:
            send_message(room_id=fileid,
                         submission_message="Track Hub set up, starting hubCheck")
        else:
            send_message(room_id=fileid,
                         submission_message="Error setting up track hub, please contact faang-dcc@ebi.ac.uk")
    return {'error_flag': error_flag, 'data': res_dict}


@app.task(base=LogErrorsTask)
def hub_check(result, fileid):
    error_flag = result['error_flag']
    res_dict = result['data']
    res_dict['HubCheck Results'] = {
        'warnings': [],
        'errors': []
    }
    if not error_flag:
        hub = res_dict['Hub Data'][0]['Name']
        cmd = f"./trackhubs/hubCheck -noTracks " \
              f"http://nginx-svc:80/files/trackhubs/{hub}/hub.txt " \
              f"> /data/{hub}/hubCheck_results.txt"
        os.system(cmd)
        with open(f'/data/{hub}/hubCheck_results.txt', 'r') as f:
            for line in f:
                if line.split()[0] != 'Found':
                    line = line.replace('http://nginx-svc:80', 'https://api.faang.org')
                    if line.split()[0] == 'warning:':
                        res_dict['HubCheck Results']['warnings'].append(line)
                    else:
                        error_flag = True
                        res_dict['HubCheck Results']['errors'].append(line)
        if not error_flag:
            send_message(room_id=fileid, validation_results=res_dict,
                         submission_message=f"Hub check successful. " \
                                            f"Track Hub set up at https://api.faang.org/files/trackhubs/{hub}/hub.txt")
        else:
            send_message(room_id=fileid, validation_results=res_dict,
                         submission_message="Error: Hub check failed")
    return {'error_flag': error_flag, 'data': res_dict}


@app.task(base=LogErrorsTask)
def register_trackhub(data, roomid):
    send_message(room_id=roomid,
                 submission_message="Registering Track Hub")
    error_flag = False
    # login and get auth token
    user = TRACKHUBS_USERNAME
    pwd = TRACKHUBS_PASSWORD
    hub_dir = data['hub_dir']
    genome_name = data['genome_name']
    genome_id = data['genome_id']
    hub_url = f"https://api.faang.org/files/trackhubs/{hub_dir}/hub.txt"
    r = requests.get('https://www.trackhubregistry.org/api/login', auth=(user, pwd), verify=True)
    if not r.ok:
        error_flag = True
    else:
        auth_token = r.json()[u'auth_token']
        # register tracks with trackhubs registry
        headers = {'user': user, 'auth_token': auth_token}
        payload = {'url': hub_url, 'assemblies': {genome_name: genome_id}}
        r = requests.post('https://www.trackhubregistry.org/api/trackhub', headers=headers, json=payload, verify=True)
        if not r.ok:
            error_flag = True
    if error_flag:
        send_message(room_id=roomid,
                     errors="Registration failed, please contact faang-dcc@ebi.ac.uk")
    else:
        send_message(room_id=roomid,
                     submission_message="Track Hub registered successfully!")
    return {'error_flag': error_flag, 'data': data}


@app.task(base=LogErrorsTask)
def associate_specimen(res_dict, roomid):
    error_flag = res_dict['error_flag']
    data = res_dict['data']
    if not error_flag:
        hub_dir = data['hub_dir']
        genome_name = data['genome_name']
        hub_url = f"https://api.faang.org/files/trackhubs/{hub_dir}/hub.txt"
        trackdb_url = f"http://nginx-svc:80/files/trackhubs/{hub_dir}/{genome_name}/trackDb.txt"
        update_payload = {"doc": {"trackhubUrl": hub_url}}
        biosample_ids = []
        response = requests.get(trackdb_url)
        text_lines = response.text.split('\n')
        for line in text_lines:
            line = line.split(' ')
            if line[0] == 'bigDataUrl':
                biosample_ids.append(line[1].split('_')[-1].split('.')[0])
        biosample_ids = list(set(biosample_ids))
        errors = []
        for id in biosample_ids:
            update_url = f"http://daphne-svc:8000/data/specimen/{id}/update"
            res = requests.put(update_url, data=json.dumps(update_payload))
            if res.status == 200:
                send_message(room_id=roomid,
                             submission_message=f"Specimen {id} linked to Track Hub succesfully")
            else:
                error_flag = True
                errors.append(f"Specimen {id} could not be linked")
        if not error_flag:
            send_message(room_id=roomid,
                         submission_message="Track Hub registered successfully!\n" \
                                            "All relevant specimen records linked to Track Hub")
        else:
            send_message(room_id=roomid, submission_results=errors,
                         errors=f"Track Hub registered.\n" \
                                "Some specimen could not be linked, please contact faang-dcc@ebi.ac.uk")
    return {'error_flag': error_flag, 'data': data}
