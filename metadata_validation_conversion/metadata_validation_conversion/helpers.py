import requests
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .constants import SAMPLE_CORE_URL, EXPERIMENT_CORE_URL, SAMPLE, EXPERIMENT, ANALYSIS, \
    ALLOWED_SHEET_NAMES, MODULE_RULES


def get_core_ruleset_json(template_type):
    """
    Get the core ruleset in the json format according to the template type
    :param template_type: the template type
    :return:
    """
    if template_type == SAMPLE:
        return requests.get(SAMPLE_CORE_URL).json()
    elif template_type == EXPERIMENT:
        return requests.get(EXPERIMENT_CORE_URL).json()
    elif template_type == ANALYSIS:
        return None


def get_ruleset_from_constants(template_type, sheet_name, constants):
    """
    Get the type ruleset in the json format according to the template type
    :param template_type: the template type
    :param sheet_name: the name of the sheet, which indicates the type of the data
    :return:
    """
    if template_type in constants and sheet_name in constants[template_type]:
        url = constants[template_type][sheet_name]
        return requests.get(url).json()
    return None


def get_type_ruleset_json(template_type, sheet_name):
    """
    Get the type ruleset in the json format according to the template type
    :param template_type: the template type
    :param sheet_name: the name of the sheet, which indicates the type of the data
    :return:
    """
    return get_ruleset_from_constants(template_type, sheet_name, ALLOWED_SHEET_NAMES)


def get_module_ruleset_json(template_type, sheet_name):
    """
    Get the type ruleset in the json format according to the template type
    :param template_type: the template type
    :param sheet_name: the name of the sheet, which indicates the type of the data
    :return:
    """

    return get_ruleset_from_constants(template_type, sheet_name, MODULE_RULES)


def get_rules_json(url, json_type, module_url=None):
    """
    Retrieve ruleset json based on the given condition
    if type is analyses, return json based on the url,
    otherwise return type rule set from url, core rule set and module rule set (if provided)
    :param url: url for type json field
    :param json_type: type of json to fetch: samples, experiments, analyses
    :param module_url: module url if appropriate
    :return: type and core json
    """
    if json_type == SAMPLE:
        core_json = SAMPLE_CORE_URL
    elif json_type == EXPERIMENT:
        core_json = EXPERIMENT_CORE_URL
    elif json_type == ANALYSIS:
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
    This function will convert any string to snake_case string
    :param my_string: string to convert
    :return: string in camel_case format
    """
    return '_'.join(my_string.lower().split(" ")).replace("'", "")


def send_message(room_id, conversion_status=None, validation_status=None,
                 submission_status=None, errors=None, validation_results=None,
                 conversion_errors=None, table_data=None,
                 annotation_status=None):
    """
    This function will send message to channel layer
    :param room_id: room id to construct ws url
    :param conversion_status: conversion status to send
    :param validation_status: validation status to send
    :param submission_status: submission status to send
    :param errors: list of errors
    :param validation_results: results of validation
    :param conversion_errors: list of conversion errors
    :param table_data: data to show the table
    :param annotation_status: annotation status to send
    """
    response = {
        'conversion_status': conversion_status,
        'validation_status': validation_status,
        'submission_status': submission_status,
        'errors': errors,
        'validation_results': validation_results,
        'conversion_errors': conversion_errors,
        'table_data': table_data,
        'annotation_status': annotation_status
    }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"submission_{room_id}", {
        "type": "submission_message",
        "response": response})
