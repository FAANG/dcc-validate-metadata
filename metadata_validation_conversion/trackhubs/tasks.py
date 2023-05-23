from abc import ABC
from elasticsearch import Elasticsearch, RequestsHttpConnection
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from collections import OrderedDict
from metadata_validation_conversion.settings import \
    TRACKHUBS_USERNAME, TRACKHUBS_PASSWORD
from django.conf import settings
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
                    id_list = row_values[5].split(',')
                    data['Related Specimen ID'] = [id.strip() for id in id_list]
                    data['Subdirectory'] = row_values[6]
                data_dict[sh.name].append(data)
        send_message(room_id=fileid, submission_message="Template converted successfully")
    except:
        send_message(room_id=fileid, submission_message="Error while converting template")
        error_flag = True
    finally:
        return {'error_flag': error_flag, 'data': data_dict}


@app.task(base=LogErrorsTask)
def validate(result, webin_credentials, fileid):
    error_flag = result['error_flag']
    if not error_flag:
        send_message(submission_message="Starting to validate file",
                     room_id=fileid)
        error_dict = {}
        data_dict = result['data']
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
                        # check that "File Path" exists in Webin FTP
                        if row_prop == 'File Path' and row_prop not in errors:
                            cmd = f"curl -r 0-1 ftp://webin.ebi.ac.uk/{data_dict[key][row_index][row_prop]} --user {webin_credentials['user']}:{webin_credentials['pwd']}"
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
                            invalid_ids = []
                            for id in data_dict[key][row_index][row_prop]:
                                url = f'http://backend-svc:8000/data/specimen/{id}'
                                res = requests.get(url)
                                if res.status_code != 200 or len(json.loads(res.content)['hits']['hits']) == 0:
                                    invalid_ids.append(id)
                            if len(invalid_ids):
                                error_flag = True
                                if len(invalid_ids) == 1:
                                    errors[row_prop] = f"{invalid_ids[0]} is not a valid FAANG Specimen ID"
                                else:
                                    errors[row_prop] = f"{', '.join(invalid_ids)} are not valid FAANG Specimen IDs"
                error_dict[key].append(errors)
        if error_flag:
            data_dict['errors'] = error_dict
            send_message(room_id=fileid, submission_message="Error: Template validation failed", validation_results=data_dict)
            return {'error_flag': error_flag, 'data': error_dict}
        else:
            send_message(room_id=fileid, submission_message="Template validation successful")
            return {'error_flag': error_flag, 'data': data_dict}
    return {'error_flag': error_flag, 'data': data_dict}


@app.task(base=LogErrorsTask)
def generate_hub_files(result, fileid, modify):
    error_flag = result['error_flag']
    res_dict = result['data']
    if not error_flag:
        hub = res_dict['Hub Data'][0]['Name']
        genome = res_dict['Genome Data'][0]['Assembly Name']
        # handle updates
        if modify == 'true':
            hub_dir = f"/usr/share/nginx/html/files/trackhubs/{hub}"
            # move existing version of trackhub
            if os.path.isdir(hub_dir):
                # if an old backup already exists, replace it
                old_hub_dir = f"/usr/share/nginx/html/files/trackhubs/{hub}_old"
                if os.path.isdir(old_hub_dir):
                    os.system(f"rm -rf old_hub_dir")
                os.system(f"mv {hub_dir} {hub_dir}_old")
                send_message(room_id=fileid, submission_message="Updating Hub files")
            # if hub dir does not exist in update workflow, display error
            else:
                error_flag = True
                send_message(room_id=fileid, submission_message=f"Error: Update failed, Track hub {hub} not found. "\
                    f"Please select 'Submit new trackhub' and re-submit to create a new track hub")
        else:
            hub_dir = f"/usr/share/nginx/html/files/trackhubs/{hub}"
            # if hub dir already exists in new submission workflow, display error
            if os.path.isdir(hub_dir):
                error_flag = True
                send_message(room_id=fileid, submission_message=f"Error: Track hub {hub} already exists, "\
                    f"please choose a different name for your track hub. If you are trying " \
                        f"to update {hub}, please select option 'Update existing trackhub' and re-submit")
            else:
                send_message(room_id=fileid, submission_message="Generating Hub files")
        if error_flag:
            return {'error_flag': error_flag, 'data': res_dict}
        else:
            try:
                file_server = 'https://api.faang.org/files/trackhubs'
                # create hub directory structure
                cmd = f"mkdir -p /usr/share/nginx/html/files/trackhubs/{hub}/{genome}"
                os.system(cmd)
                file_server_path = "/usr/share/nginx/html/files/trackhubs"
                # generate hub.txt
                with open(f'{file_server_path}/{hub}/hub.txt', 'w') as f:
                    f.write(f"hub {res_dict['Hub Data'][0]['Name']}\n")
                    f.write(f"shortLabel {res_dict['Hub Data'][0]['Short Label']}\n")
                    f.write(f"longLabel {res_dict['Hub Data'][0]['Long Label']}\n")
                    f.write("genomesFile genomes.txt\n")
                    f.write(f"email {res_dict['Hub Data'][0]['Email']}\n")
                    if res_dict['Hub Data'][0]['Description File Path']:
                        f.write(f"descriptionUrl {res_dict['Hub Data'][0]['Description File Path']}\n")
                # generate genomes.txt
                with open(f'{file_server_path}/{hub}/genomes.txt', 'w') as f:
                    f.write(f"genome {res_dict['Genome Data'][0]['Assembly Name']}\n")
                    f.write(f"trackDb {res_dict['Genome Data'][0]['Assembly Name']}/trackDb.txt\n")
                    if res_dict['Genome Data'][0]['Description']:
                        f.write(f"description {res_dict['Genome Data'][0]['Description']}\n")
                    if res_dict['Genome Data'][0]['Organism']:
                        f.write(f"organism {res_dict['Genome Data'][0]['Organism']}\n")
                # generate trackDb.txt
                with open(f'{file_server_path}/{hub}/{genome}/trackDb.txt', 'w') as f:
                    for row in res_dict['Tracks Data']:
                        file_name = row['File Path'].split('/')[-1]
                        track_url = f"{file_server}/{hub}/{genome}/{row['Subdirectory']}/{file_name}"
                        f.write(f"track {row['Track Name']}\n")
                        f.write(f"bigDataUrl {track_url}\n")
                        f.write(f"shortLabel {row['Short Label']}\n")
                        f.write(f"longLabel {row['Long Label']}\n")
                        f.write(f"type {row['File Type']}\n\n")

                # backup files to s3
                files = [f"{genome}/trackDb.txt", "hub.txt", "genomes.txt"]
                for file in files:
                    cmd = f"aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 cp " \
                            f"{file_server_path}/{hub}/{file} s3://trackhubs/{hub}/{file}"
                    os.system(cmd)

                send_message(room_id=fileid,
                            submission_message="Track Hub files generated")
            except:
                error_flag = True
                send_message(room_id=fileid,
                            submission_message="Error generating Track Hub files, please contact faang-dcc@ebi.ac.uk")
            finally:
                return {'error_flag': error_flag, 'data': res_dict}
    return {'error_flag': error_flag, 'data': res_dict}


@app.task(base=LogErrorsTask)
def upload_files(result, webin_credentials, fileid):
    error_flag = result['error_flag']
    res_dict = result['data']
    if not error_flag:
        send_message(room_id=fileid, submission_message="Setting up Track Hub")
        hub = res_dict['Hub Data'][0]['Name']
        genome = res_dict['Genome Data'][0]['Assembly Name']
        try:
            # upload track files to trackhubs local storage
            for track in res_dict['Tracks Data']:
                file = track['File Path'].split('/')[-1]
                # create sub-directories
                os.system(f"mkdir -p /usr/share/nginx/html/files/trackhubs/{hub}/{genome}/{track['Subdirectory']}")
                # download files from webin FTP area of user
                filepath = f"/usr/share/nginx/html/files/trackhubs/{hub}/{genome}/{track['Subdirectory']}/{file}"
                cmd = f"curl -s ftp://webin.ebi.ac.uk/{track['File Path']} --user {webin_credentials['user']}:{webin_credentials['pwd']} -o {filepath}"
                os.system(cmd)
                # backup files to s3
                cmd = f"aws --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 cp " \
                        f"{filepath} s3://trackhubs/{hub}/{genome}/{track['Subdirectory']}/{file}"
                os.system(cmd)
            send_message(room_id=fileid,
                         submission_message="Track Hub set up, starting hubCheck")
        except:
            error_flag = True
            send_message(room_id=fileid,
                         submission_message="Error setting up track hub, please contact faang-dcc@ebi.ac.uk")
        finally:
            return {'error_flag': error_flag, 'data': res_dict}
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
        os.system(f"mkdir -p /data/{hub}")
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
def update_es_records(data, roomid):
    error_flag = False
    send_message(room_id=roomid,
                 submission_message="Updating Track Hub records")
    try:
        # get hub data
        trackhub_data = {
            'name': data['Hub Data'][0]['Name'],
            'shortLabel': data['Hub Data'][0]['Short Label'],
            'longLabel': data['Hub Data'][0]['Long Label'],
            'email': data['Hub Data'][0]['Email']
        }
        # get genome data
        trackhub_data['genome'] = {
            'gcaAccession': data['Genome Data'][0]['Assembly Accession'],
            'ensemblAssemblyName': data['Genome Data'][0]['Assembly Name']
        }
        # get tracks data
        sub_dirs = {}
        file_server = 'https://api.faang.org/files/trackhubs'
        hub = data['Hub Data'][0]['Name']
        genome = data['Genome Data'][0]['Assembly Name']
        for track in data['Tracks Data']:
            file_name = track['File Path'].split('/')[-1]
            track_data = {
                "track": track['Track Name'],
                "bigDataUrl": f"{file_server}/{hub}/{genome}/{track['Subdirectory']}/{file_name}",
                "shortLabel": track['Short Label'],
                "longLabel": track['Long Label'],
                "type": track['File Type']
            }
            if track['Subdirectory'] in sub_dirs:
                sub_dirs[track['Subdirectory']].append(track_data)
            else:
                sub_dirs[track['Subdirectory']] = [track_data]
        sub_dirs_list = []
        for sub_dir, tracks in sub_dirs.items():
            sub_dirs_list.append({
                'name': sub_dir,
                'tracks': tracks
            })
        trackhub_data['subdirectories'] = sub_dirs_list
        # create ES record
        es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection, \
            http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=True)
        es.index(index='trackhubs', id=trackhub_data['name'], body=trackhub_data)
        send_message(room_id=roomid,
                        submission_message="Updated track hub records")
    except:
        error_flag = True
        send_message(room_id=roomid,
                        submission_message="Error updating track hub records, please contact faang-dcc@ebi.ac.uk")
    finally:
        return {'error_flag': error_flag, 'data': data}

def update_trackhub(hub_dir, headers, payload):
    # fetch all trackhubs associated with the account
    r = requests.get("https://www.trackhubregistry.org/api/trackhub", headers=headers, verify=True)
    hubs = json.loads(r.content)
    # get the trackhub ID associated with hub_dir
    for hub in hubs:
        if hub['name'] == hub_dir:
            hub_id = hub['hub_id']
            # update the hub registration for hub_dir
            r = requests.put(f"https://www.trackhubregistry.org/api/trackhub/{hub_id}", headers=headers, json=payload, verify=True)
            if r.ok:
                return True
    return False

@app.task(base=LogErrorsTask)
def register_trackhub(res, roomid):
    send_message(room_id=roomid,
                 submission_message="Registering Track Hub")
    error_flag = res['error_flag']
    data = res['data']
    # login and get auth token
    user = TRACKHUBS_USERNAME
    pwd = TRACKHUBS_PASSWORD
    hub_dir = data['Hub Data'][0]['Name']
    genome_name = data['Genome Data'][0]['Assembly Name']
    genome_id = data['Genome Data'][0]['Assembly Accession']
    hub_url = f"https://api.faang.org/files/trackhubs/{hub_dir}/hub.txt"
    login_payload = {"username": user, "password": pwd}
    r = requests.post('https://www.trackhubregistry.org/api/login', data=login_payload)
    if not r.ok:
        error_flag = True
    else:
        auth_token = r.json()[u'auth_token']
        # register tracks with trackhubs registry
        headers = {'user': user, 'Authorization': 'Token ' + auth_token}
        payload = {'url': hub_url, 'assemblies': {genome_name: genome_id}}
        r = requests.post('https://www.trackhubregistry.org/api/trackhub', headers=headers, json=payload, verify=True)
        if not r.ok:
            # if hub is already registered, update the hub registration
            error_flag = not update_trackhub(hub_dir, headers, payload)
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
        hub_dir = data['Hub Data'][0]['Name']
        gen_acc = data['Genome Data'][0]['Assembly Accession']
        hub_url = f"https://www.ncbi.nlm.nih.gov/genome/gdv/browser/genome/?acc={gen_acc}" \
            f"&hub=https://api.faang.org/files/trackhubs/{hub_dir}/hub.txt"
        update_payload = { "doc": { "trackhubUrl": hub_url } }
        biosample_ids = []
        for track in data['Tracks Data']:
            biosample_ids = biosample_ids + track['Related Specimen ID']
            biosample_ids = list(set(biosample_ids))
        errors = []
        es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection, http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=True)
        try:
            for id in biosample_ids:
                es_data = es.update(index='specimen', id=id, body=update_payload)
            send_message(room_id=roomid,
                         submission_message="Track Hub registered successfully!\n" \
                                            "All relevant specimen records linked to Track Hub")
        except:
            error_flag = True
            send_message(room_id=roomid, submission_results=errors,
                         errors=f"Track Hub registered.\n" \
                                "Some specimen could not be linked, please contact faang-dcc@ebi.ac.uk")
        finally:
            return {'error_flag': error_flag, 'data': data}
    return {'error_flag': error_flag, 'data': data}
