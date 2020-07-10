import requests
import json
from requests.auth import HTTPBasicAuth

from metadata_validation_conversion.constants import AAP_TEST_SERVER, \
    AAP_PROD_SERVER, SUBMISSION_TEST_SERVER, SUBMISSION_PROD_SERVER


class BioSamplesSubmission:
    def __init__(self, username, password, json_to_submit, mode):
        self.username = username
        self.password = password
        self.json_to_submit = json_to_submit
        self.domain_name = None
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

    def get_header(self):
        """
        This function will return header required for every request to server
        :return: header as dict
        """
        token = self.get_token()
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/hal+json',
            'Authorization': f'Bearer {token}'
        }
        return headers

    def create_domain(self, name, description):
        """
        This function will create domain
        :param name: name of the domain
        :param description: description of the domein
        :return:
        """
        domain_data = {
            'domainName': name,
            'domainDesc': description
        }
        domain_data = json.dumps(domain_data)
        create_domain_response = requests.post(f"{self.aap_server}/domains",
                                               headers=self.get_header(),
                                               data=domain_data)
        if create_domain_response.status_code != 201:
            # TODO: Send Error message to front-end
            return 'Error'

    def choose_domain(self):
        """
        This function will return existing domain names
        :return: dict of domain names under domainName key
        """
        choose_domain_response = requests.get(f"{self.aap_server}/my/domains",
                                              headers=self.get_header())
        # TODO: check required status code
        if choose_domain_response.status_code != 200:
            # TODO: Send Error message to front-end
            return 'Error'
        # TODO: send these message to front-end
        return choose_domain_response.json()

    def submit_records(self):
        if self.domain_name is None:
            # TODO: send these message to front-end
            return 'Error'
        biosamples_ids = dict()
        # submit record
        for item in self.json_to_submit:
            item['domain'] = self.domain_name
            del item['relationships']
            name = item['name']
            item = json.dumps(item)
            create_submission_response = requests.post(
                f"{self.submission_server}/biosamples/samples",
                headers=self.get_header(),
                data=item)
            if create_submission_response.status_code != 201:
                # TODO: send these message to front-end
                return 'Error'
            biosamples_ids[name] = create_submission_response.json()[
                'accession']

        # update relationship part of records
        for item in self.json_to_submit:
            if len(item['relationships']) > 0:
                for relationship in item['relationships']:
                    if relationship['source'] in biosamples_ids:
                        relationship['source'] = biosamples_ids[
                            relationship['source']]
                    if relationship['target'] in biosamples_ids:
                        relationship['target'] = biosamples_ids[
                            relationship['target']]
                id = biosamples_ids[item['name']]
                item['accession'] = id
                item['domain'] = self.domain_name
                item = json.dumps(item)
                create_submission_response = requests.put(
                    f"{self.submission_server}/biosamples/samples/{id}",
                    headers=self.get_header(),
                    data=item)
                if create_submission_response.status_code != 200:
                    # TODO: send these message to front-end
                    return 'Error'
