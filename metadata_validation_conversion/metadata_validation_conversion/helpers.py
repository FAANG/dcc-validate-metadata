import requests
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .constants import SAMPLE_CORE_URL, EXPERIMENT_CORE_URL


def get_rules_json(url, json_type, module_url=None):
    """
    This function will fetch json from url and then fetch core json from $ref
    :param url: url for type json field
    :param json_type: type of json to fetch: samples, experiments, analyses
    :param module_url: module url if appropriate
    :return: type and core json
    """
    if json_type == 'samples':
        core_json = SAMPLE_CORE_URL
    elif json_type == 'experiments':
        core_json = EXPERIMENT_CORE_URL
    elif json_type == 'analyses':
        return requests.get(url).json()
    else:
        raise ValueError(f"Error: {json_type} is not allowed type!")
    type_json = requests.get(url).json()
    core_json = requests.get(core_json).json()
    if module_url:
        module_json = requests.get(module_url).json()
        return type_json, core_json, module_json
    else:
        return type_json, core_json


def convert_to_snake_case(my_string):
    """
    This function will convert any string to camel_case string
    :param my_string: string to convert
    :return: string in camel_case format
    """
    return '_'.join(my_string.lower().split(" ")).replace("'", "")


def send_message(conversion_status=None, validation_status=None, errors=None,
                 validation_results=None):
    """
    This function will send message to channel layer
    :param conversion_status: converstion status to send
    :param validation_status: validation status to send
    :param errors: list of errors
    :param validation_results: results of validation
    """
    response = {
        'conversion_status': conversion_status,
        'validation_status': validation_status,
        'errors': errors,
        'validation_results': validation_results
    }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("submission_test_task", {
        "type": "submission_message",
        "response": response})
