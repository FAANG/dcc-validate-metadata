from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from .BiosamplesFileConverter import BiosamplesFileConverter
from .BiosamplesSubmission import BioSamplesSubmission
from .AnalysesFileConverter import AnalysesFileConverter
from .ExperimentsFileConverter import ExperimentFileConverter
from .AnnotateTemplate import AnnotateTemplate

import json


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
def submit_to_biosamples(results, credentials, room_id):
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
            biosamples=submission_results,
            submission_message="Success: submission was completed",
            room_id=room_id)
        submission_data = ''
        for k, v in submission_results.items():
            submission_data += f"{k}\t{v}\n"
        return submission_data


@app.task
def generate_annotated_template(json_to_convert, room_id, data_type):
    annotation_results = AnnotateTemplate(json_to_convert, room_id, data_type)
    annotation_results.start_conversion()
    send_message(annotation_status='Download data', room_id=room_id)
    return 'Success'


@app.task
def prepare_samples_data(json_to_convert, room_id):
    conversion_results = BiosamplesFileConverter(json_to_convert[0])
    results = conversion_results.start_conversion()
    send_message(submission_status='Data is ready', room_id=room_id)
    return results


@app.task
def prepare_analyses_data(json_to_convert, room_id):
    conversion_results = AnalysesFileConverter(json_to_convert[0])
    analysis_xml, submission_xml = conversion_results.start_conversion()
    send_message(submission_status='Data is ready', room_id=room_id)
    return 'analysis', analysis_xml, submission_xml


@app.task
def prepare_experiments_data(json_to_convert, room_id):
    conversion_results = ExperimentFileConverter(json_to_convert[0], room_id)
    experiment_xml, run_xml, study_xml, submission_xml = \
        conversion_results.start_conversion()
    if 'Error' in experiment_xml:
        send_message(submission_status='Failed to convert data',
                     conversion_errors=experiment_xml, room_id=room_id)
    elif 'Error' in run_xml:
        send_message(submission_status='Failed to convert data',
                     conversion_errors=run_xml, room_id=room_id)
    elif 'Error' in study_xml:
        send_message(submission_status='Failed to convert data',
                     conversion_errors=study_xml, room_id=room_id)
    elif 'Error' in submission_xml:
        send_message(submission_status='Failed to convert data',
                     conversion_errors=submission_xml, room_id=room_id)
    else:
        send_message(submission_status='Data is ready', room_id=room_id)
    return 'experiment', experiment_xml, run_xml, study_xml, submission_xml
