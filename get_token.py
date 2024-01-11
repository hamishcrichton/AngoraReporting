import requests


def get_angora_token():

    data = {
        'client_id': '8f6f9757-0d0e-4201-8aa9-cac37821ac17',
        'scope': 'https://api.businesscentral.dynamics.com/.default',
        'client_secret': '_X58Q~xrLeofWwoSc~PUKy_aPG7ZRtxXoyO.manj',
        'grant_type': 'client_credentials',
    }

    response = requests.post('https://login.microsoftonline.com/7b8264b4-3685-4886-ae48-15ef08b9f0ea/oauth2/v2.0/token', data=data)
    if response.status_code != 200:
        raise Exception(f'Request failed with status code {response.status_code}')
    return response.json()['access_token']

hc = get_angora_token()


