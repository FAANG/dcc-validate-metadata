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
    This function will convert any string to snake_case string
    :param my_string: string to convert
    :return: string in camel_case format
    """
    return '_'.join(my_string.lower().split(" ")).replace("'", "")


def send_message(room_id, conversion_status=None, validation_status=None,
                 submission_status=None, errors=None, validation_results=None,
                 conversion_errors=None, table_data=None,
                 annotation_status=None, domains=None,
                 submission_message=None, submission_results=None,
                 bovreg_submission=None):
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
    :param domains: list of user domains
    :param submission_message: submission message to send
    :param submission_results: list of submission results
    :param bovreg_submission: true if secondary_project == BovReg
    """
    response = {
        'conversion_status': conversion_status,
        'validation_status': validation_status,
        'submission_status': submission_status,
        'submission_message': submission_message,
        'errors': errors,
        'validation_results': validation_results,
        'conversion_errors': conversion_errors,
        'table_data': table_data,
        'annotation_status': annotation_status,
        'domains': domains,
        'submission_results': submission_results,
        'bovreg_submission': bovreg_submission
    }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"submission_{room_id}", {
        "type": "submission_message",
        "response": response})


def send_message_graphql(task_id, graphql_status=None, errors=None):
    response = {
        'graphql_status': graphql_status,
        'errors': errors
    }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"graphqltaskstatus-{task_id}", {
        "type": "graphql_task_result",
        "response": response})
