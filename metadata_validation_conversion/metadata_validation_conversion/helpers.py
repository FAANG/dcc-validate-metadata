import requests
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .constants import SAMPLE_CORE_URL


def get_samples_json(url):
    """
    This function will fetch json from url and then fetch core json from $ref
    :param url: url for type json field
    :return: type and core json
    """
    samples_type_json = requests.get(url).json()
    samples_core_json = requests.get(SAMPLE_CORE_URL).json()
    return samples_type_json, samples_core_json


def convert_to_snake_case(my_string):
    """
    This function will convert any string to camel_case string
    :param my_string: string to convert
    :return: string in camel_case format
    """
    return '_'.join(my_string.lower().split(" "))


def send_message(status, errors=None, validation_results=None):
    """
    This function will send message to channel layer
    :param status: status to send
    :param errors: list of errors
    :param validation_results: results of validation
    """
    response = {
        'status': status,
        'errors': errors,
        'validation_results': validation_results
    }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("submission_test_task", {
        "type": "submission_message",
        "response": response})
