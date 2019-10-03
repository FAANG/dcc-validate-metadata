import requests
from .constants import SAMPLE_CORE_URL


def get_samples_json(url):
    """
    This function will fetch json from url and then fetch core json from $ref
    :param url: url for type json fiel
    :return: type and core json
    """
    samples_type_json = requests.get(url).json()
    samples_core_json = requests.get(SAMPLE_CORE_URL).json()
    return samples_type_json, samples_core_json
