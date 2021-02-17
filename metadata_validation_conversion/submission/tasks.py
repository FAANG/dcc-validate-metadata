import subprocess
import json

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


@app.task
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


@app.task
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


@app.task
def prepare_samples_data(json_to_convert, room_id, private=False):
    conversion_results = BiosamplesFileConverter(json_to_convert[0], private)
    results = conversion_results.start_conversion()
    send_message(submission_status='Data is ready', room_id=room_id)
    return results


@app.task
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


@app.task
def prepare_analyses_data(json_to_convert, room_id, private=False):
    conversion_results = AnalysesFileConverter(json_to_convert[0], room_id)
    xml_files = list()
    analysis_xml, submission_xml = conversion_results.start_conversion()
    xml_files.extend([analysis_xml, submission_xml])
    for xml_file in xml_files:
        if 'Error' in xml_file:
            send_message(submission_message='Failed to convert data',
                         conversion_errors=xml_file, room_id=room_id)
            return 'Error'
    send_message(submission_status='Data is ready', room_id=room_id)
    return 'Success'


@app.task
def prepare_experiments_data(json_to_convert, room_id, private=False):
    conversion_results = ExperimentFileConverter(json_to_convert[0], room_id,
                                                 private)
    xml_files = list()
    # generate submission.xml for study submission and another submission.xml
    # for other xml files submission
    if private:
        study_xml = conversion_results.generate_study_xml()
        private_study_submission_xml = \
            conversion_results.generate_submission_xml(
                private_study_submission=True
            )
        submission_xml = conversion_results.generate_submission_xml()
        run_xml = conversion_results.generate_run_xml()
        experiment_xml = conversion_results.generate_experiment_xml()
        xml_files.append(private_study_submission_xml)
    else:
        experiment_xml, run_xml, study_xml, submission_xml = \
            conversion_results.start_conversion()
    xml_files.extend([experiment_xml, run_xml, study_xml, submission_xml])
    for xml_file in xml_files:
        if 'Error' in xml_file:
            send_message(submission_message='Failed to convert data',
                         conversion_errors=xml_file, room_id=room_id)
            return 'Error'
    send_message(submission_status='Data is ready', room_id=room_id)
    return 'Success'


@app.task
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
    if submission_type == 'experiments':
        experiment_xml = f"{room_id}_experiment.xml"
        run_xml = f"{room_id}_run.xml"
        study_xml = f"{room_id}_study.xml"
        # Private data hubs submission
        if credentials['private_submission']:
            # 1. submit study and parse study id
            private_submission_xml = f"{room_id}_private_study_submission.xml"
            submit_to_ena_process = subprocess.run(
                f'curl -u {BOVREG_USERNAME}:{BOVREG_PASSWORD} '
                f'-F "SUBMISSION=@{private_submission_xml}" '
                f'-F "STUDY=@{study_xml}" '
                f'"{submission_path}"',
                shell=True, capture_output=True)
            submission_results = parse_submission_results(
                submit_to_ena_process.stdout, room_id)
            if submission_results == 'Error':
                return 'Error'
            study_id = fetch_project_id(submit_to_ena_process.stdout)
            # 2. link study id with private data hub
            project_json = {
                "projectId": study_id,
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
            # 3. submit other xml files referencing this study
            # Change internal study id on study id that we got in step 1
            sub_command = f's/<STUDY_REF refname=.*>/<STUDY_REF ' \
                          f'refname="{study_id}">/g'
            change_study_id_process = subprocess.run(f"sed -i '{sub_command}' "
                                                     f"{experiment_xml}",
                                                     shell=True,
                                                     capture_output=True)
            # submit experiment and run xml
            if change_study_id_process.returncode != 0:
                send_message(
                    submission_message="Error: submission failed",
                    submission_results=[[],
                                        ["Couldn't change internal study id"]],
                    room_id=room_id)
                return 'Error'
            submit_to_ena_process = subprocess.run(
                f'curl -u {BOVREG_USERNAME}:{BOVREG_PASSWORD} '
                f'-F "SUBMISSION=@{submission_xml}" '
                f'-F "EXPERIMENT=@{experiment_xml}" '
                f'-F "RUN=@{run_xml}" '
                f'"{submission_path}"',
                shell=True, capture_output=True
            )
        # Public submission
        else:
            submit_to_ena_process = subprocess.run(
                f'curl -u {credentials["username"]}:{credentials["password"]} '
                f'-F "SUBMISSION=@{submission_xml}" '
                f'-F "EXPERIMENT=@{experiment_xml}" '
                f'-F "RUN=@{run_xml}" '
                f'-F "STUDY=@{study_xml}" '
                f'"{submission_path}"',
                shell=True, capture_output=True)
    else:
        # Should work for both private and public submission
        analysis_xml = f"{room_id}_analysis.xml"
        submit_to_ena_process = subprocess.run(
            f'curl -u {credentials["username"]}:{credentials["password"]} '
            f'-F "SUBMISSION=@{submission_xml}" '
            f'-F "ANALYSIS=@{analysis_xml}" '
            f'"{submission_path}"',
            shell=True, capture_output=True)

    submission_results = submit_to_ena_process.stdout
    _ = parse_submission_results(submission_results, room_id)
    # subprocess.run(f"rm {room_id}*.xml", shell=True)
    return submission_results.decode('utf-8')


def fetch_project_id(submission_results):
    """
    This function returns project id from receipt xml
    :param submission_results: stdout string from subprocess
    :return: project id in format 'PRJEB20767'
    """
    root = etree.fromstring(submission_results)
    return root.find('STUDY').attrib['accession']


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


@app.task
def generate_annotated_template(json_to_convert, room_id, data_type):
    annotation_results = AnnotateTemplate(json_to_convert, room_id, data_type)
    annotation_results.start_conversion()
    send_message(annotation_status='Download data', room_id=room_id)
    return 'Success'
