import time
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from .BiosamplesFileConverter import BiosamplesFileConverter
from .AnalysesFileConverter import AnalysesFileConverter
from .ExperimentsFileConverter import ExperimentFileConverter
from .helpers import zip_files


@app.task
def prepare_samples_data(json_to_convert):
    conversion_results = BiosamplesFileConverter(json_to_convert)
    results = conversion_results.start_conversion()
    send_message(submission_status='Data is ready')
    return results


@app.task
def prepare_analyses_data(json_to_convert):
    conversion_results = AnalysesFileConverter(json_to_convert)
    analysis_xml, submission_xml = conversion_results.start_conversion()
    send_message(submission_status='Data is ready')
    return 'analysis', analysis_xml, submission_xml


@app.task
def prepare_experiments_data(json_to_convert):
    conversion_results = ExperimentFileConverter(json_to_convert)
    results = conversion_results.start_conversion()
    send_message(submission_status='Data is ready')
    return results
