import requests
import json
from requests.auth import HTTPBasicAuth

from metadata_validation_conversion.constants import AAP_TEST_SERVER, \
    AAP_PROD_SERVER, SUBMISSION_TEST_SERVER, SUBMISSION_PROD_SERVER


class BioSamplesSubmission:
    def __init__(self, username, password, json_to_submit, mode, domain=None):
        self.username = username
        self.password = password
        self.json_to_submit = json_to_submit
        self.domain_name = domain
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

    def get_user_reference(self):
        """
        This function will get user reference from BioSamples
        :return: user reference as a string
        """
        get_user_response = requests.get(
            f"{self.aap_server}/users/{self.username}",
            headers=self.get_header())
        if get_user_response.status_code != 200:
            return f"Error: {get_user_response.json()['message']}"
        return get_user_response.json()['userReference']

    def get_domain_reference(self):
        """
        This function will get domain reference from BioSamples
        :return: domain reference as a string
        """
        get_domain_response = requests.get(f"{self.aap_server}/my/management",
                                           headers=self.get_header())
        if get_domain_response.status_code != 200:
            return f"Error: {get_domain_response.json()['message']}"
        return get_domain_response.json()['domainReference']

    def create_domain(self, name, description):
        """
        This function will create domain
        :param name: name of the domain
        :param description: description of the domain
        :return: error in case of wrong status code
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
            return f"Error: {create_domain_response.json()['message']}"
        # Adding user to created domain
        return self.add_user_to_domain(
            create_domain_response.json()['domainReference'])

    def add_user_to_domain(self, domain_reference):
        """
        This function will add current user to created domain
        :param: domain_reference: domain reference as a string
        :return:
        """
        user_reference = self.get_user_reference()
        if 'Error' in user_reference:
            return user_reference
        add_user_to_domain_response = requests.put(
            f"{self.aap_server}/domains/{domain_reference}/{user_reference}/"
            f"user", headers=self.get_header())
        if add_user_to_domain_response.status_code != 200:
            return f"Error: {add_user_to_domain_response.json()['message']}"
        return "Success: new domain was created and current user was " \
               "added to this domain"

    def choose_domain(self):
        """
        This function will return existing domain names
        :return: list of domain names
        """
        domains = list()
        choose_domain_response = requests.get(
            f"{self.aap_server}/my/domains", headers=self.get_header())
        if choose_domain_response.status_code != 200:
            return f"Error: {choose_domain_response.json()['message']}"
        for domain in choose_domain_response.json():
            domains.append(domain['domainName'])
        return domains

    def submit_records(self):
        if self.domain_name is None:
            return 'Error: domain name was not specified'
        biosamples_ids = dict()
        # create a copy as we need to delete relationships part from dict
        for item in self.json_to_submit:
            tmp = dict()
            for key, value in item.items():
                if key != 'relationships':
                    tmp[key] = value
            tmp['domain'] = self.domain_name
            name = tmp['name']
            tmp = json.dumps(tmp)
            create_submission_response = requests.post(
                f"{self.submission_server}/biosamples/samples",
                headers=self.get_header(),
                data=tmp)
            if create_submission_response.status_code != 201:
                return 'Error: record was not submitted to BioSamples, ' \
                       'please contact faang-dcc@ebi.ac.uk'
            biosamples_ids[name] = create_submission_response.json()[
                'accession']

        # update relationship part of records
        for item in self.json_to_submit:
            if 'relationships' in item and len(item['relationships']) > 0:
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
                    return 'Error: relationship part was not updated, ' \
                           'please contact faang-dcc@ebi.ac.uk'
        return biosamples_ids
