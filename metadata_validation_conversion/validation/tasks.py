from metadata_validation_conversion.celery import app


@app.task
def validate_against_schema(json_to_test):
    return f"This is results of conversion: {json_to_test}"
