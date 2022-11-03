import os
from django.conf import settings
from django.urls import reverse
import requests
from requests import Request, Session
from requests.exceptions import MissingSchema

from .enums import RoleChoices


MBERKAS_OAUTH_TOKEN_URL = 'https://mberkas.unhas.ac.id/oauth/token'
MBERKAS_OAUTH_BEARER = ''

MHS_PROFILE_URL = "https://customapi.neosia.unhas.ac.id/GetProfilMhs"
DOSEN_PROFILE_URL = ""
ADMIN_PROFILE_URL = ""


def get_user_profile(user: dict, role: str):
    """Get user's profile

    Args:
        user (str): User's data
        role (str): User's role

    Returns:
        dict: JSON response from Neosia API
    """

    parameters = {}
    headers = {
        "token": os.environ.get("NEOSIA_API_TOKEN")
    }

    # Request authenticated user's profile
    match(role):
        case RoleChoices.ADMIN_PRODI:
            response = request_data_to_neosia(ADMIN_PROFILE_URL, parameters, headers)
        case RoleChoices.DOSEN:
            response = request_data_to_neosia(DOSEN_PROFILE_URL, parameters, headers)
        case RoleChoices.MAHASISWA:
            parameters["nim"] = user['username']
            response = request_data_to_neosia(MHS_PROFILE_URL, parameters, headers)
    
    if response is None: return None

    if response.status_code == 200:
        json_response = response.json()

        # Return None if the request has no data
        if len(json_response["data"]) == 0: return None
        
        user_profile = json_response["data"][0]
        return user_profile
    else:
        print(response)
        return None

def request_data_to_neosia(auth_url: str, parameters: dict, headers: dict):
    """Request data to Neosia API

    Args:
        auth_url (str): Target URL
        parameters (dict): Requested parameters
        headers (dict): Requested headers

    Returns:
        Response: Response from Neosia API
    """

    try:
        response = requests.post(auth_url, params=parameters, headers=headers)
    except MissingSchema:
        return None
    return response

def get_oauth_access_token(code: str):
    """Get OAuth Access Token from MBerkas OAuth

    Args:
        code (str): Code from OAuth

    Returns:
        str: Access token
    """

    redirect_uri = os.environ.get('DJANGO_ALLOWED_HOST') + reverse('accounts:oauth-callback')
    parameters = {
        'grant_type': 'authorization_code',
        'client_id': '3',
        'client_secret': os.environ.get('OAUTH_CLIENT_SECRET'),
        'redirect_uri': 'http://{}'.format(redirect_uri),
        'code': code,
    }
    
    req = Request(
        'POST',
        MBERKAS_OAUTH_TOKEN_URL,
        files={
            'grant_type': (None, parameters['grant_type']),
            'client_id': (None, parameters['client_id']),
            'client_secret': (None, parameters['client_secret']),
            'redirect_uri': (None, parameters['redirect_uri']),
            'code': (None, code),
        }
    ).prepare()
    s = Session()
    response = s.send(req)
    access_token = response.json().get('access_token')
    
    return access_token

def validate_user(access_token: str):
    """Validate user from MBerkas OAuth Bearer with given access token

    Args:
        access_token (str): Access token from MBerkas OAuth

    Returns:
        dict: User's data
    """

    if access_token is None: return None

    response = requests.get(MBERKAS_OAUTH_BEARER, headers={
        'Authorization': 'Bearer {}'.format(access_token)
    })

    if response.status_code == 200:
        user = response.json()
        return user
    else:
        if settings.DEBUG: print(response.raw)
        return None
