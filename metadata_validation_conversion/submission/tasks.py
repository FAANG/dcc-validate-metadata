import time
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from .BiosamplesFileConverter import BiosamplesFileConverter
from .AnalysesFileConverter import AnalysesFileConverter
from .ExperimentsFileConverter import ExperimentFileConverter


@app.task
def prepare_samples_data(json_to_convert):
    conversion_results = BiosamplesFileConverter(json_to_convert)
    results = conversion_results.start_conversion()
    send_message(submission_status='Data is ready')
    return results


@app.task
def prepare_analyses_data(json_to_convert):
    conversion_results = AnalysesFileConverter(json_to_convert)
    results = conversion_results.start_conversion()
    send_message(submission_status='Data is ready')
    return results


@app.task
def prepare_experiments_data(json_to_convert):
    conversion_results = ExperimentFileConverter(json_to_convert)
    results = conversion_results.start_conversion()
    send_message(submission_status='Data is ready')
    return results
