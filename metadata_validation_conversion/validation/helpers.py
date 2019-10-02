import requests


def validate(data):
    url = 'https://raw.githubusercontent.com/FAANG/dcc-metadata/' \
          'switch_to_json-schema/json_schema/core/samples/' \
          'faang_samples_core.metadata_rules.json'
    schema = requests.get(url).json()
    json_to_send = {
        'schema': schema,
        'object': data
    }
    response = requests.post(
        'http://localhost:3020/validate', json=json_to_send).json()
    print(response['validationState'])
