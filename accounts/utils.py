from django.conf import settings
from requests.exceptions import MissingSchema
import os
import requests

from .enums import RoleChoices


MHS_AUTH_URL = "https://customapi.neosia.unhas.ac.id/checkMahasiswa2"
MHS_PROFILE_URL = "https://customapi.neosia.unhas.ac.id/GetProfilMhs"

DOSEN_AUTH_URL = ""
DOSEN_PROFILE_URL = ""

ADMIN_AUTH_URL = ""
ADMIN_PROFILE_URL = ""

def validate_user(username: str, password: str, role: str):
    """Validate authenticated user in Neosia API

    Args:
        username (str): User's username
        password (str): User's password
        role (str): User's role

    Returns:
        dict: JSON response from Neosia API
    """

    parameters = {
        "username": username,
        "password": password
    }
    headers = {
        "token": os.environ.get("NEOSIA_API_TOKEN")
    }

    # Request authenticated user's data
    match(role):
        case RoleChoices.ADMIN_PRODI:
            response = request_data_to_neosia(ADMIN_AUTH_URL, parameters, headers)
        case RoleChoices.DOSEN:
            response = request_data_to_neosia(DOSEN_AUTH_URL, parameters, headers)
        case RoleChoices.MAHASISWA:
            response = request_data_to_neosia(MHS_AUTH_URL, parameters, headers)

    if response is None: return None

    if response.status_code == 200:
        json_response = response.json()

        # Return None if the request is not success
        if json_response["success"] == "0": return None
        
        user = json_response["data"]
        return user
    else:
        if settings.DEBUG: print(response.raw)
        return None

def get_user_profile(username:str, role: str):
    """Get user's profile

    Args:
        username (str): User's username
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
            parameters["nim"] = username
            response = request_data_to_neosia(MHS_PROFILE_URL, parameters, headers)
    
    if response is None: return None

    if response.status_code == 200:
        json_response = response.json()

        # Return None if the request has no data
        if len(json_response["data"]) == 0: return None
        
        user_profile = json_response["data"][0]
        return user_profile
    else:
        if settings.DEBUG: print(response.raw)
        return None

def request_data_to_neosia(auth_url: str, params: dict, headers: dict):
    """Request data to Neosia API

    Args:
        auth_url (str): Target URL
        params (dict): Requested parameters
        headers (dict): Requested headers

    Returns:
        Response: Response from Neosia API
    """

    try:
        response = requests.post(auth_url, params=params, headers=headers)
    except MissingSchema:
        if settings.DEBUG: print('There are no response')
        return None
    except requests.exceptions.SSLError:
        if settings.DEBUG: print("SSL Error")
        response = requests.post(auth_url, params=params, headers=headers, verify=False)
    return response
