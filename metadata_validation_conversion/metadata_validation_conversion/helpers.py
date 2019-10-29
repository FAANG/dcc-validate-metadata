import requests
import asyncio
import websockets
import json
from .constants import SAMPLE_CORE_URL, WS_URL


def get_samples_json(url):
    """
    This function will fetch json from url and then fetch core json from $ref
    :param url: url for type json fiel
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


def send_message(status):
    """
    This function will call send_message_to_ws in async loop
    :param status: status to send
    """
    asyncio.get_event_loop().run_until_complete(send_message_to_ws(status))


async def send_message_to_ws(status):
    """
    This function will send status to ws server
    :param status: status to send
    :return:
    """
    async with websockets.connect(WS_URL) as websocket:
        await websocket.send(json.dumps({'status': status}))
