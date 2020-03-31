import time
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from .BiosamplesFileConverter import BiosamplesFileConverter
from .AnalysesFileConverter import AnalysesFileConverter
from .ExperimentsFileConverter import ExperimentFileConverter
from .AnnotateTemplate import AnnotateTemplate
from .helpers import zip_files


@app.task
def generate_annotated_template(json_to_convert, room_id, data_type):
    annotation_results = AnnotateTemplate(json_to_convert, room_id, data_type)
    annotation_results.start_conversion()
    send_message(annotation_status='Download data', room_id=room_id)
    return 'Success'


@app.task
def prepare_samples_data(json_to_convert, room_id):
    conversion_results = BiosamplesFileConverter(json_to_convert)
    results = conversion_results.start_conversion()
    send_message(submission_status='Data is ready', room_id=room_id)
    return results


@app.task
def prepare_analyses_data(json_to_convert, room_id):
    conversion_results = AnalysesFileConverter(json_to_convert)
    analysis_xml, submission_xml = conversion_results.start_conversion()
    send_message(submission_status='Data is ready', room_id=room_id)
    return 'analysis', analysis_xml, submission_xml


@app.task
def prepare_experiments_data(json_to_convert, room_id):
    conversion_results = ExperimentFileConverter(json_to_convert[0])
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
