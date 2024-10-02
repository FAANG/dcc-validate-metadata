import copy
from datetime import datetime
import requests
import json

from metadata_validation_conversion.constants import WEBIN_TEST_SERVER, WEBIN_PROD_SERVER, SUBMISSION_TEST_SERVER, SUBMISSION_PROD_SERVER


class WebinBioSamplesSubmission:
    def __init__(self, username, password, json_to_submit, mode):
        self.username = username
        self.password = password
        self.json_to_submit = json_to_submit
        if mode == 'test':
            self.webin_server = WEBIN_TEST_SERVER
            self.submission_server = SUBMISSION_TEST_SERVER
        elif mode == 'prod':
            self.webin_server = WEBIN_PROD_SERVER
            self.submission_server = SUBMISSION_PROD_SERVER

    def get_token(self):
        """
        This function will return token to be used upon every request to server
        :return: token as a string object
        """
        url = f"{self.webin_server}/token?ttl=5"

        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json'
        }

        data = {
            "authRealms": [
                "ENA"
            ],
            "password": self.password,
            "username": self.username
        }

        response = requests.post(url, headers=headers, json=data)

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

    def submit_records(self):
        biosamples_ids = dict()
        # create a copy as we need to delete relationships part from dict
        for item in self.json_to_submit:
            tmp = dict()
            for key, value in item.items():
                if key != 'relationships':
                    tmp[key] = value
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
            if ('relationships' in item and len(item['relationships']) > 0
                    and item['relationships'][0]['target'] != 'restricted access'):
                for relationship in item['relationships']:
                    if relationship['source'] in biosamples_ids:
                        relationship['source'] = biosamples_ids[
                            relationship['source']]
                    if relationship['target'] in biosamples_ids:
                        relationship['target'] = biosamples_ids[
                            relationship['target']]
                id = biosamples_ids[item['name']]
                item['accession'] = id
                item = json.dumps(item)
                create_submission_response = requests.put(
                    f"{self.submission_server}/biosamples/samples/{id}",
                    headers=self.get_header(),
                    data=item)
                if create_submission_response.status_code != 200:
                    return 'Error: relationship part was not updated, ' \
                           'please contact faang-dcc@ebi.ac.uk'
        return biosamples_ids

    def fetch_biosample_data(self, id):
        response = requests.get(f"{self.submission_server}/biosamples"
                                f"/samples/{id}").json()
        return response

    def update_records(self):
        if self.domain_name is None:
            return 'Error: domain name was not specified'

        updated_biosamples_ids = dict()

        for item in self.json_to_submit:
            tmp = dict()
            for key, value in item.items():
                # replace name with accession for update
                if key == 'name':
                    tmp['accession'] = value
                else:
                    tmp[key] = value

            tmp['domain'] = self.domain_name
            tmp['update'] = str(datetime.now().isoformat())
            accession = tmp['accession']

            # fetch the existing entry from the database
            existing_biosample_entry = self.fetch_biosample_data(accession)

            if existing_biosample_entry:
                """
                In BioSamples, updating a sample overwrites its existing content with the new one. 
                To preserve existing attributes, first download the sample, 
                build a new version including existing and new attributes, and resubmit the new content.
                """
                updated_biosample_entry = copy.deepcopy(existing_biosample_entry)
                tmp['characteristics']['sample name'] = existing_biosample_entry['characteristics']['sample name']

                if 'derived from' in tmp['characteristics']:
                    # replace with sample name it is derived from
                    derived_from_biosampleid = tmp['characteristics']['derived from']
                    derived_from_name = list()

                    for id in derived_from_biosampleid:
                        if id['text'] in updated_biosamples_ids:
                            derived_from_name.append({'text': updated_biosamples_ids[id['text']]})
                        else:
                            derivedfrom_biosample_entry = self.fetch_biosample_data(id['text'])
                            if derivedfrom_biosample_entry:
                                derived_from_name.append({'text': derivedfrom_biosample_entry['name']})
                            else:
                                return f"Error: derived_from BioSample Id ({id['text']}) is incorrect , " \
                                       "please contact faang-dcc@ebi.ac.uk"

                    tmp['characteristics']['derived from'] = derived_from_name

                updated_biosample_entry['characteristics'] = tmp['characteristics']
                updated_biosample_entry['organization'] = tmp['organization']
                updated_biosample_entry['contact'] = tmp['contact']
                updated_biosample_entry['update'] = tmp['update']
                updated_biosample_entry['relationships'] = tmp['relationships']
                updated_json = json.dumps(updated_biosample_entry)

                update_submission_response = requests.put(
                    f"{self.submission_server}/biosamples/samples/{accession}",
                    headers=self.get_header(),
                    data=updated_json)

                if update_submission_response.status_code != 200:
                    return 'Error: relationship part was not updated, ' \
                           'please contact faang-dcc@ebi.ac.uk'

                updated_biosamples_ids[accession] = update_submission_response.json()[
                    'name']

        reverted_updated_biosamples_ids = dict((v, k) for k, v in updated_biosamples_ids.items())
        return reverted_updated_biosamples_ids
