import requests

from requests.auth import HTTPBasicAuth

from metadata_validation_conversion.settings import \
    BOVREG_BIOSAMPLES_PASSWORD_PROD


def check_field_existence(field_to_check, record_to_check):
    """
    This function will check for existence of field in record
    :param field_to_check: field to search for
    :param record_to_check: record to search field in
    :return:
    """
    if field_to_check in record_to_check \
            and record_to_check[field_to_check] != "":
        return record_to_check[field_to_check]
    else:
        return None


def remove_underscores(value_to_convert):
    """
    This function will return value without underscores
    :param value_to_convert: value to convert
    :return: value with spaces instead of underscores
    """
    return " ".join(value_to_convert.split("_"))


def convert_to_uppercase(value_to_convert):
    """
    This function will convert column names to uppercase
    :param value_to_convert: value to be converted
    :return: value in uppercase
    """
    return ' '.join([word.capitalize() for word in value_to_convert.split('_')])


def get_credentials(credentials):
    """
    This function will return username and password from the request
    :param credentials: body of request with credentials data
    :return: username and password
    """
    username = credentials['username']
    password = credentials['password']
    return username, password


def get_token():
    response = requests.get(
        f"https://api.aai.ebi.ac.uk/auth",
        auth=HTTPBasicAuth(
            "BovRegProd", BOVREG_BIOSAMPLES_PASSWORD_PROD))
    return response.text


def get_header():
    """
    This function will return header required for every request to server
    :return: header as dict
    """
    token = get_token()
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/hal+json',
        'Authorization': f'Bearer {token}'
    }
    return headers
