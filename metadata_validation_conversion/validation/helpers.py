import requests


def validate(data, schema):
    json_to_send = {
        'schema': schema,
        'object': data
    }
    response = requests.post(
        'http://localhost:3020/validate', json=json_to_send).json()
    if 'validationState' in response and response['validationState'] == 'VALID':
        return response['validationState']
    else:
        return response
