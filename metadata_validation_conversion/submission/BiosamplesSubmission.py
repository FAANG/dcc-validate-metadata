import requests
import json
from requests.auth import HTTPBasicAuth

from metadata_validation_conversion.constants import AAP_TEST_SERVER, \
    AAP_PROD_SERVER, SUBMISSION_TEST_SERVER, SUBMISSION_PROD_SERVER


class BioSamplesSubmission:
    def __init__(self, username, password, mode):
        self.username = username
        self.password = password
        if mode == 'test':
            self.aap_server = AAP_TEST_SERVER
            self.submission_server = SUBMISSION_TEST_SERVER
        elif mode == 'prod':
            self.aap_server = AAP_PROD_SERVER
            self.submission_server = SUBMISSION_PROD_SERVER

    def get_token(self):
        """
        This function will return token to be used upon every request to server
        :return: token as a string object
        """
        response = requests.get(
            f"{self.aap_server}/auth",
            auth=HTTPBasicAuth(self.username, self.password))
        return response.text

    def create_domain(self):
        pass

    def choose_domain(self):
        pass

    def submit_records(self):
        pass

    def update_records(self):
        pass