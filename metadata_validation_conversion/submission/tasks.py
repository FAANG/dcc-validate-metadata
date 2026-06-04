import subprocess
import json
import re
import os
from abc import ABC
from datetime import datetime
from lxml import etree
from elasticsearch import Elasticsearch, RequestsHttpConnection
from django.http import HttpResponse
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from metadata_validation_conversion.constants import ENA_TEST_SERVER, \
    ENA_PROD_SERVER
from .BiosamplesFileConverter import BiosamplesFileConverter
from .WebinBiosamplesSubmission import WebinBioSamplesSubmission
from .BiosamplesSubmission import BioSamplesSubmission
from .AnalysesFileConverter import AnalysesFileConverter
from .ExperimentsFileConverter import ExperimentFileConverter
from .AnnotateTemplate import AnnotateTemplate
from .helpers import get_credentials
from celery import Task
from django.conf import settings
# from deepdiff import DeepDiff

es = Elasticsearch([settings.NODE], connection_class=RequestsHttpConnection,
                   http_auth=(settings.ES_USER, settings.ES_PASSWORD), use_ssl=True, verify_certs=True)


class LogErrorsTask(Task, ABC):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        send_message(room_id=kwargs['room_id'], submission_message='Error with the submission process',
                     errors=f'Error: {exc}')


@app.task(base=LogErrorsTask)
def get_domains(credentials, room_id):
    send_message(submission_message="Waiting: getting information about "
                                    "existing domains", room_id=room_id)
    username, password = get_credentials(credentials)
    biosamples_submission = BioSamplesSubmission(username, password, {},
                                                 credentials['mode'])
    domains = biosamples_submission.choose_domain()
    if 'Error' in domains:
        send_message(submission_message=domains, room_id=room_id)
    else:
        send_message(
            domains=domains,
            submission_message='Success: got information about existing '
                               'domains', room_id=room_id)
    return 'Success'


@app.task(base=LogErrorsTask)
def submit_new_domain(credentials, room_id):
    username, password = get_credentials(credentials)
    biosamples_submission = BioSamplesSubmission(username, password, {},
                                                 credentials['mode'])
    create_domain_results = biosamples_submission.create_domain(
        credentials['domain_name'], credentials['domain_description'])
    send_message(submission_message=create_domain_results, room_id=room_id)
    domains = biosamples_submission.choose_domain()
    if 'Error' in domains:
        send_message(submission_message=domains, room_id=room_id)
    else:
        send_message(
            domains=domains,
            submission_message='Success: got information about existing '
                               'domains', room_id=room_id)
    return 'Success'


@app.task(base=LogErrorsTask)
def prepare_samples_data(json_to_convert, room_id, action='submission', mode='prod'):
    conversion_results = BiosamplesFileConverter(json_to_convert[0], mode, action)
    results = conversion_results.start_conversion()
    send_message(submission_status='Data is ready', room_id=room_id)
    return results


@app.task(base=LogErrorsTask)
def submit_to_biosamples(results, credentials, room_id, action="submission"):
    send_message(
        submission_message="Waiting: submitting records to BioSamples",
        room_id=room_id)
    username, password = get_credentials(credentials)

    if username.startswith("Webin"):
        submission = WebinBioSamplesSubmission(
            username, password, results[0], credentials['mode']
        )
    else:
        submission = BioSamplesSubmission(
            username, password, results[0], credentials['mode'], credentials['domain_name']
        )

    if action == 'update':
        submission_results = submission.update_records()
    else:
        submission_results = submission.submit_records()

    if 'Error' in submission_results:
        send_message(submission_message=submission_results, room_id=room_id)
        return 'Error'
    else:
        send_message(
            submission_results=submission_results,
            submission_message=f"Success: {action} was completed",
            room_id=room_id)
        submission_data = ''
        for k, v in submission_results.items():
            submission_data += f"{k}\t{v}\n"
        return submission_data


@app.task(base=LogErrorsTask)
def prepare_analyses_data(json_to_convert, room_id, action='submission'):
    conversion_results = AnalysesFileConverter(json_to_convert[0], room_id,
                                               action)
    xml_files = list()
    analysis_xml, submission_xml, sample_xml = \
        conversion_results.start_conversion()
    xml_files.extend([analysis_xml, submission_xml])
    for xml_file in xml_files:
        if 'Error' in xml_file:
            send_message(submission_message='Error: Failed to convert data',
                         errors=xml_file, room_id=room_id)
            return 'Error'
    send_message(submission_status='Data is ready', room_id=room_id)
    return 'Success'


@app.task(base=LogErrorsTask)
def prepare_experiments_data(json_to_convert, room_id, action='submission'):
    conversion_results = ExperimentFileConverter(json_to_convert[0], room_id,
                                                 action)
    xml_files = list()
    experiment_xml, run_xml, study_xml, submission_xml, sample_xml = \
        conversion_results.start_conversion()
    xml_files.extend([experiment_xml, run_xml, study_xml, submission_xml])
    if sample_xml is not None:
        xml_files.append(sample_xml)
    for xml_file in xml_files:
        if 'Error' in xml_file:
            send_message(submission_message='Error: Failed to convert data',
                         errors=xml_file, room_id=room_id)
            return 'Error'
    send_message(submission_status='Data is ready', room_id=room_id)
    return 'Success'


@app.task(base=LogErrorsTask)
def submit_data_to_ena(results, credentials, room_id, submission_type, action="submission"):
    if results[0] != 'Success':
        return 'Error'
    send_message(submission_message='Waiting: submitting records to ENA',
                 room_id=room_id)
    submission_path = ENA_TEST_SERVER if credentials['mode'] == 'test' else \
        ENA_PROD_SERVER
    submission_xml = f"{room_id}_submission.xml"

    username = credentials["username"]
    password = credentials["password"]
    # User-supplied credentials are passed as argv (shell=False) so they
    # cannot break out into the shell (CWE-78).
    if submission_type == 'experiments':
        experiment_xml = f"{room_id}_experiment.xml"
        run_xml = f"{room_id}_run.xml"
        study_xml = f"{room_id}_study.xml"
        submit_to_ena_process = subprocess.run(
            ["curl", "-u", f"{username}:{password}",
             "-F", f"SUBMISSION=@{submission_xml}",
             "-F", f"EXPERIMENT=@{experiment_xml}",
             "-F", f"RUN=@{run_xml}",
             "-F", f"STUDY=@{study_xml}",
             submission_path],
            capture_output=True)
    elif submission_type == 'analyses':
        analysis_xml = f"{room_id}_analysis.xml"
        submit_to_ena_process = subprocess.run(
            ["curl", "-u", f"{username}:{password}",
             "-F", f"SUBMISSION=@{submission_xml}",
             "-F", f"ANALYSIS=@{analysis_xml}",
             submission_path],
            capture_output=True)

    submission_results = submit_to_ena_process.stdout
    parse_submission_results(submission_results, submission_type, room_id, action)
    # TODO: uncomment after testing
    # subprocess.run(f"rm {room_id}*.xml", shell=True)
    return submission_results.decode('utf-8')


def parse_submission_results(submission_results, submission_type, room_id, action="submission"):
    """
    This function parses submission response
    :param submission_results: submission response
    :param submission_type: submission type
    :param room_id: room id to send messages through django channels
    :param action: indicates whether submission to ENA was an update or a new submission
    :return: error and info messages
    """
    if 'Access Denied' in submission_results.decode('utf-8'):
        send_message(submission_message="Error: Access Denied", room_id=room_id)
        return 'Error'
    else:
        root = etree.fromstring(submission_results)
        submission_error_messages = list()
        submission_info_messages = list()
        for messages in root.findall('MESSAGES'):
            for error in messages.findall('ERROR'):
                submission_error_messages.append(error.text)
            for info in messages.findall('INFO'):
                submission_info_messages.append(info.text)
        if len(submission_error_messages) > 0:
            send_message(submission_message=f"Error: {action} failed",
                         submission_results=[submission_info_messages,
                                             submission_error_messages],
                         room_id=room_id)
            return 'Error'
        else:
            # Save submission data to ES
            save_submission_data(root, submission_type, room_id, action)
            send_message(
                submission_message=f"Success: {action} was successful",
                submission_results=[submission_info_messages],
                room_id=room_id)
            return 'Success'


def parse_experiments_data(root, submission_id, action):
    object_types = {
        'EXPERIMENT': 'experiments',
        'STUDY': 'studies',
        'PROJECT': 'studies'
    }
    study_objs = []
    if root.get('success') == 'true':
        # get alias and accessions
        submission = root.findall('SUBMISSION')[0]
        submission_data = {
            'alias': submission.get('alias') if submission.get('alias') else '',
            'accession': submission.get('accession') if submission.get('accession') else ''
        }
        for type in object_types:
            objects = root.findall(type)
            if len(objects):
                prop = object_types[type]
                submission_data[prop] = []
                for object in objects:
                    obj_data = {
                        'alias': object.get('alias') if object.get('alias') else ''
                    }
                    if prop == 'studies':
                        obj_data['accession'] = object.findall('EXT_ID')[0].get('accession')
                    else:
                        obj_data['accession'] = object.get('accession')
                    submission_data[prop].append(obj_data)

        # iterate through each study
        for study in submission_data['studies']:
            study_obj = {
                'study_id': study['accession'],
                'study_alias': study['alias'],
                'experiments': [],
                'available_in_portal': 'false'
            }
            current_date = datetime.today().strftime('%Y-%m-%d')
            if action == 'submission':
                study_obj.update({"submission_date": current_date})

            if action == 'update':
                study_obj.update({"update_date": current_date})

            # get experiments associated with each study
            experiment_xml = f'{submission_id}_experiment.xml'
            if os.path.exists(experiment_xml):
                experiment_root = etree.parse(experiment_xml).getroot()
                experiments = experiment_root.findall('EXPERIMENT')
                exp_alias_list = []
                assay_types = []
                secondary_projects = []
                for exp in experiments:
                    exp_study_alias = exp.findall('STUDY_REF')[0].get('refname')
                    # check that the study reference for the experiment matches the study
                    if exp_study_alias == study['alias']:
                        for experiment in submission_data['experiments']:
                            # get experiment accession from submission data using experiment alias
                            if experiment['alias'] == exp.get('alias'):
                                study_obj['experiments'].append({
                                    'alias': experiment['alias'],
                                    'accession': experiment['accession'],
                                    'available_in_portal': 'false'
                                })
                                exp_alias_list.append(experiment['alias'])

                        # get assay type and secondary project
                        attributes = exp.findall('EXPERIMENT_ATTRIBUTES')
                        if len(attributes):
                            attributes = attributes[0].findall('EXPERIMENT_ATTRIBUTE')
                            for attribute in attributes:
                                tag = attribute.findall('TAG')[0].text
                                if tag == 'assay type':
                                    assay_types.append(attribute.findall('VALUE')[0].text)
                                elif tag == 'secondary project':
                                    secondary_projects.append(attribute.findall('VALUE')[0].text)
                study_obj['assay_type'] = ', '.join(set(assay_types))
                study_obj['secondary_project'] = ', '.join(set(secondary_projects))
            study_objs.append(study_obj)
    return study_objs
        
        
def parse_analysis_data(root, submission_id, action):
    study_objs = []
    if root.get('success') == 'true':
        objects = root.findall('ANALYSIS')
        if len(objects):
            analyses_objs = {}
            for object in objects:
                # get analyses alias and accession
                analysis_alias = object.get('alias')
                analysis_accession = object.get('accession') if object.get('accession') else ''
                analyses_objs[analysis_alias] = {
                    'alias': analysis_alias,
                    'accession': analysis_accession,
                    'study_id': '',
                    'assay_type': '',
                    'secondary_project': ''
                }
            analysis_xml = f'{submission_id}_analysis.xml'
            if os.path.exists(analysis_xml):
                analysis_root = etree.parse(analysis_xml).getroot()
                analyses = analysis_root.findall('ANALYSIS')
                for a in analyses:
                    a_alias = a.get('alias')
                    # get study_id
                    analyses_objs[a_alias]['study_id'] = a.findall('STUDY_REF')[0].get('accession')
                    # get assay_type and secondary_project
                    attributes = a.findall('ANALYSIS_ATTRIBUTES')
                    if len(attributes):
                        attributes = attributes[0].findall('ANALYSIS_ATTRIBUTE')
                        for attribute in attributes:
                            tag = attribute.findall('TAG')[0].text
                            if tag == 'Assay Type':
                                analyses_objs[a_alias]['assay_type'] = attribute.findall('VALUE')[0].text
                            elif tag == 'Secondary Project':
                                analyses_objs[a_alias]['secondary_project'] = attribute.findall('VALUE')[0].text
            study_objs_dict = {}
            for analysis in analyses_objs.values():
                if analysis['study_id'] not in study_objs_dict:
                    study_objs_dict[analysis['study_id']] = {
                        'study_id': analysis['study_id'],
                        'study_alias': '',
                        'assay_type': [],
                        'secondary_project': [],
                        'analyses': [],
                        'available_in_portal': 'false'
                    }
                    current_date = datetime.today().strftime('%Y-%m-%d')
                    if action == 'submission':
                        study_objs_dict[analysis['study_id']].update({"submission_date": current_date})

                    if action == 'update':
                        study_objs_dict[analysis['study_id']].update({"update_date": current_date})

                study_objs_dict[analysis['study_id']]['analyses'].append({
                    'alias': analysis['alias'],
                    'accession': analysis['accession'],
                    'available_in_portal': 'false'
                })
                study_objs_dict[analysis['study_id']]['assay_type'].append(analysis['assay_type'])
                study_objs_dict[analysis['study_id']]['secondary_project'].append(analysis['secondary_project'])

            for study_obj in study_objs_dict.values():
                study_obj['assay_type'] = ', '.join(set(study_obj['assay_type']))
                study_obj['secondary_project'] = ', '.join(set(study_obj['secondary_project']))
            study_objs = study_objs_dict.values()
    return study_objs


def save_submission_data(root, submission_type, room_id, action):
    if root.get('success') == 'true':
        if submission_type == 'experiments':
            study_objs = parse_experiments_data(root, room_id, action)
        else:
            study_objs = parse_analysis_data(root, room_id, action)
        for study_obj in study_objs:
            existing_doc = get_doc(study_obj['study_id'])
            if existing_doc is not None:
                # retain submission_date field
                study_obj['submission_date'] = existing_doc['submission_date']
            es.index(index='submissions', id=study_obj['study_id'], body=study_obj)


def get_doc(study_id):
    filters = {'query': {'bool': {'filter': [{'terms': {'study_id': [study_id]}}]}}}
    query = json.dumps(filters)
    data = es.search(index='submissions', size=1, from_=0, track_total_hits=True, body=json.loads(query))
    if len(data['hits']['hits']) > 0 and data['hits']['hits'][0]['_source']:
        return data['hits']['hits'][0]['_source']
    return None


@app.task(base=LogErrorsTask)
def generate_annotated_template(json_to_convert, room_id, data_type, action):
    annotation_results = AnnotateTemplate(json_to_convert, room_id, data_type, action)
    annotation_results.start_conversion()
    send_message(annotation_status='Download data', room_id=room_id)
    return 'Success'
