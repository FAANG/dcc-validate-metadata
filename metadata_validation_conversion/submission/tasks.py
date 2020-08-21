import subprocess

from lxml import etree

from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from metadata_validation_conversion.constants import ENA_TEST_SERVER, \
    ENA_PROD_SERVER
from .BiosamplesFileConverter import BiosamplesFileConverter
from .BiosamplesSubmission import BioSamplesSubmission
from .AnalysesFileConverter import AnalysesFileConverter
from .ExperimentsFileConverter import ExperimentFileConverter
from .AnnotateTemplate import AnnotateTemplate


@app.task
def get_domains(credentials, room_id):
    send_message(submission_message="Waiting: getting information about "
                                    "existing domains", room_id=room_id)
    biosamples_submission = BioSamplesSubmission(credentials['username'],
                                                 credentials['password'],
                                                 {}, credentials['mode'])
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
    biosamples_submission = BioSamplesSubmission(credentials['username'],
                                                 credentials['password'],
                                                 {}, credentials['mode'])
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
def prepare_samples_data(json_to_convert, room_id):
    conversion_results = BiosamplesFileConverter(json_to_convert[0])
    results = conversion_results.start_conversion()
    send_message(submission_status='Data is ready', room_id=room_id)
    return results


@app.task
def submit_to_biosamples(results, credentials, room_id):
    send_message(
        submission_message="Waiting: submitting records to BioSamples",
        room_id=room_id)
    biosamples_submission = BioSamplesSubmission(credentials['username'],
                                                 credentials['password'],
                                                 results[0],
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
def prepare_analyses_data(json_to_convert, room_id):
    conversion_results = AnalysesFileConverter(json_to_convert[0], room_id)
    analysis_xml, submission_xml = conversion_results.start_conversion()
    send_message(submission_status='Data is ready', room_id=room_id)
    return 'Success'


@app.task
def prepare_experiments_data(json_to_convert, room_id):
    conversion_results = ExperimentFileConverter(json_to_convert[0], room_id)
    experiment_xml, run_xml, study_xml, submission_xml = \
        conversion_results.start_conversion()
    if 'Error' in experiment_xml:
        send_message(submission_message='Failed to convert data',
                     conversion_errors=experiment_xml, room_id=room_id)
    elif 'Error' in run_xml:
        send_message(submission_message='Failed to convert data',
                     conversion_errors=run_xml, room_id=room_id)
    elif 'Error' in study_xml:
        send_message(submission_message='Failed to convert data',
                     conversion_errors=study_xml, room_id=room_id)
    elif 'Error' in submission_xml:
        send_message(submission_message='Failed to convert data',
                     conversion_errors=submission_xml, room_id=room_id)
    else:
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
        submit_to_ena_process = subprocess.run(
            f'curl -u {credentials["username"]}:{credentials["password"]} '
            f'-F "SUBMISSION=@{submission_xml}" '
            f'-F "EXPERIMENT=@{experiment_xml}" '
            f'-F "RUN=@{run_xml}" '
            f'-F "STUDY=@{study_xml}" '
            f'"{submission_path}"',
            shell=True, capture_output=True)
    else:
        analysis_xml = f"{room_id}_analysis.xml"
        submit_to_ena_process = subprocess.run(
            f'curl -u {credentials["username"]}:{credentials["password"]} '
            f'-F "SUBMISSION=@{submission_xml}" '
            f'-F "ANALYSIS=@{analysis_xml}" '
            f'"{submission_path}"',
            shell=True, capture_output=True)

    submission_error_messages = list()
    submission_info_messages = list()
    submission_results = submit_to_ena_process.stdout
    if 'Access Denied' in submission_results.decode('utf-8'):
        send_message(submission_message="Error: Access Denied", room_id=room_id)
    else:
        root = etree.fromstring(submission_results)
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
        else:
            send_message(
                submission_message="Success: submission was successful",
                room_id=room_id)
    subprocess.run(f"rm {room_id}*.xml", shell=True)
    return submission_results.decode('utf-8')


@app.task
def generate_annotated_template(json_to_convert, room_id, data_type):
    annotation_results = AnnotateTemplate(json_to_convert, room_id, data_type)
    annotation_results.start_conversion()
    send_message(annotation_status='Download data', room_id=room_id)
    return 'Success'
