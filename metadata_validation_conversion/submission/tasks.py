import time
from metadata_validation_conversion.celery import app
from metadata_validation_conversion.helpers import send_message
from .BiosamplesFileConverter import BiosamplesFileConverter


@app.task
def prepare_samples_data(json_to_convert):
    conversion_results = BiosamplesFileConverter(json_to_convert)
    results = conversion_results.start_conversion()
    send_message(submission_status='Data is ready')
    return results
