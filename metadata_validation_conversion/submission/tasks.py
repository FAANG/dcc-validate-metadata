import subprocess
import json
import re

from lxml import etree

from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from metadata_validation_conversion.constants import ENA_TEST_SERVER, \
    ENA_PROD_SERVER
from metadata_validation_conversion.settings import BOVREG_USERNAME, \
    BOVREG_PASSWORD
from .BiosamplesFileConverter import BiosamplesFileConverter
from .BiosamplesSubmission import BioSamplesSubmission
from .AnalysesFileConverter import AnalysesFileConverter
from .ExperimentsFileConverter import ExperimentFileConverter
from .AnnotateTemplate import AnnotateTemplate
from .helpers import get_credentials
from celery import Task
from celery.utils.log import get_task_logger
from celery.signals import after_setup_logger
import logging
import os.path

APP_PATH = os.path.dirname(os.path.realpath(__file__))
logger = get_task_logger(__name__)

@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(f'{APP_PATH}/logs.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)


class LogErrorsTask(Task):
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
def prepare_samples_data(json_to_convert, room_id, private=False):
    conversion_results = BiosamplesFileConverter(json_to_convert[0], private)
    results = conversion_results.start_conversion()
    send_message(submission_status='Data is ready', room_id=room_id)
    return results


@app.task(base=LogErrorsTask)
def submit_to_biosamples(results, credentials, room_id):
    send_message(
        submission_message="Waiting: submitting records to BioSamples",
        room_id=room_id)
    username, password = get_credentials(credentials)
    biosamples_submission = BioSamplesSubmission(username, password, results[0],
                                                 credentials['mode'],
                                                 credentials['domain_name'])
    submission_results = biosamples_submission.submit_records()
    if 'Error' in submission_results:
        send_message(submission_message=submission_results, room_id=room_id)
        return 'Error'
    else:
        send_message(
            submission_results=submission_results,
            submission_message="Success: submission was completed",
            room_id=room_id)
        submission_data = ''
        for k, v in submission_results.items():
            submission_data += f"{k}\t{v}\n"
        return submission_data


@app.task(base=LogErrorsTask)
def prepare_analyses_data(json_to_convert, room_id, private=False):
    conversion_results = AnalysesFileConverter(json_to_convert[0], room_id,
                                               private)
    xml_files = list()
    analysis_xml, submission_xml, sample_xml = \
        conversion_results.start_conversion()
    xml_files.extend([analysis_xml, submission_xml])
    for xml_file in xml_files:
        if 'Error' in xml_file:
            send_message(submission_message='Failed to convert data',
                         conversion_errors=xml_file, room_id=room_id)
            return 'Error'
    send_message(submission_status='Data is ready', room_id=room_id)
    return 'Success'


@app.task(base=LogErrorsTask)
def prepare_experiments_data(json_to_convert, room_id, private=False):
    conversion_results = ExperimentFileConverter(json_to_convert[0], room_id,
                                                 private)
    xml_files = list()
    experiment_xml, run_xml, study_xml, submission_xml, sample_xml = \
        conversion_results.start_conversion()
    xml_files.extend([experiment_xml, run_xml, study_xml, submission_xml])
    if sample_xml is not None:
        xml_files.append(sample_xml)
    for xml_file in xml_files:
        if 'Error' in xml_file:
            send_message(submission_message='Failed to convert data',
                         conversion_errors=xml_file, room_id=room_id)
            return 'Error'
    send_message(submission_status='Data is ready', room_id=room_id)
    return 'Success'


@app.task(base=LogErrorsTask)
def submit_data_to_ena(results, credentials, room_id, submission_type):
    if results[0] != 'Success':
        send_message(submission_message="Error: submission failed",
                     room_id=room_id)
        return 'Success'
    send_message(submission_message='Waiting: submitting records to ENA',
                 room_id=room_id)
    submission_path = ENA_TEST_SERVER if credentials['mode'] == 'test' else \
        ENA_PROD_SERVER
    submission_xml = f"{room_id}_submission.xml"

    # Use BOVREG private account or get credentials from request
    if credentials['private_submission']:
        username = BOVREG_USERNAME
        password = BOVREG_PASSWORD
    else:
        username = credentials["username"]
        password = credentials["password"]
    # public experiments submission
    if submission_type == 'experiments' and \
            not credentials['private_submission']:
        experiment_xml = f"{room_id}_experiment.xml"
        run_xml = f"{room_id}_run.xml"
        study_xml = f"{room_id}_study.xml"
        password = re.escape(password)
        submit_to_ena_process = subprocess.run(
            f'curl -u {username}:{password} '
            f'-F "SUBMISSION=@{submission_xml}" '
            f'-F "EXPERIMENT=@{experiment_xml}" '
            f'-F "RUN=@{run_xml}" '
            f'-F "STUDY=@{study_xml}" '
            f'"{submission_path}"',
            shell=True, capture_output=True)
    # private experiments submission
    elif submission_type == 'experiments' and credentials['private_submission']:
        experiment_xml = f"{room_id}_experiment.xml"
        run_xml = f"{room_id}_run.xml"
        study_xml = f"{room_id}_study.xml"
        sample_xml = f"{room_id}_sample.xml"
        password = re.escape(password)
        submit_to_ena_process = subprocess.run(
            f'curl -u {username}:{password} '
            f'-F "SUBMISSION=@{submission_xml}" '
            f'-F "EXPERIMENT=@{experiment_xml}" '
            f'-F "RUN=@{run_xml}" '
            f'-F "STUDY=@{study_xml}" '
            f'-F "SAMPLE=@{sample_xml}" '
            f'"{submission_path}"',
            shell=True, capture_output=True)
    elif submission_type == 'analyses' \
            and not credentials['private_submission']:
        analysis_xml = f"{room_id}_analysis.xml"
        submit_to_ena_process = subprocess.run(
            f'curl -u {username}:{password} '
            f'-F "SUBMISSION=@{submission_xml}" '
            f'-F "ANALYSIS=@{analysis_xml}" '
            f'"{submission_path}"',
            shell=True, capture_output=True)
    elif submission_type == 'analyses' and credentials['private_submission']:
        # Submit analysis
        analysis_xml = f"{room_id}_analysis.xml"
        sample_xml = f"{room_id}_sample.xml"
        submit_to_ena_process = subprocess.run(
            f'curl -u {username}:{password} '
            f'-F "SUBMISSION=@{submission_xml}" '
            f'-F "ANALYSIS=@{analysis_xml}" '
            f'-F "SAMPLE=@{sample_xml}" '
            f'"{submission_path}"',
            shell=True, capture_output=True)

    submission_results = submit_to_ena_process.stdout
    parsed_results = parse_submission_results(submission_results, room_id)

    # Adding project to the private data hub
    if parsed_results == 'Success' and credentials['private_submission'] \
            and submission_type == 'experiments':
        project_id = fetch_project_id(submit_to_ena_process.stdout)
        project_json = {
            "projectId": project_id,
            "dcc": "dcc_korman"
        }
        with open(f"{room_id}_project.json", 'w') as w:
            json.dump(project_json, w)
        link_study_process = subprocess.run(
            f'curl -X POST --header "Content-Type: application/json" '
            f'--header "Accept: application/json" '
            f'-u "{BOVREG_USERNAME}:{BOVREG_PASSWORD}" '
            f'-d @{room_id}_project.json '
            f'"https://www.ebi.ac.uk/ena/portal/ams/webin/project/add"',
            shell=True, capture_output=True)
        if 'errorMessage' in link_study_process.stdout.decode('utf-8'):
            error_message = json.loads(
                link_study_process.stdout.decode('utf-8'))['errorMessage']
            send_message(
                submission_message="Error: submission failed",
                submission_results=[[],
                                    [error_message]],
                room_id=room_id)
            return 'Error'
    # TODO: uncomment after testing
    # subprocess.run(f"rm {room_id}*.xml", shell=True)
    return submission_results.decode('utf-8')


def fetch_project_id(submission_results):
    """
    This function returns project id from receipt xml
    :param submission_results: stdout string from subprocess
    :return: project id in format 'PRJEB20767'
    """
    root = etree.fromstring(submission_results)
    return root.find('STUDY').find('EXT_ID').attrib['accession']


def parse_submission_results(submission_results, room_id):
    """
    This function parses submission response
    :param submission_results: submission response
    :param room_id: room id to send messages through django channels
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
            send_message(submission_message="Error: submission failed",
                         submission_results=[submission_info_messages,
                                             submission_error_messages],
                         room_id=room_id)
            return 'Error'
        else:
            send_message(
                submission_message="Success: submission was successful",
                submission_results=[submission_info_messages],
                room_id=room_id)
            return 'Success'


@app.task(base=LogErrorsTask)
def generate_annotated_template(json_to_convert, room_id, data_type):
    annotation_results = AnnotateTemplate(json_to_convert, room_id, data_type)
    annotation_results.start_conversion()
    send_message(annotation_status='Download data', room_id=room_id)
    return 'Success'
