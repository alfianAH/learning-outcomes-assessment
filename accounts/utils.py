import os
import requests
from requests.exceptions import MissingSchema

from .enums import RoleChoices


MHS_AUTH_URL = "https://customapi.neosia.unhas.ac.id/checkMahasiswa2"
DOSEN_AUTH_URL = ""
ADMIN_AUTH_URL = ""

def validate_user(username: str, password: str, role: str):
    parameters = {
        "username": username,
        "password": password
    }
    headers = {
        "token": os.environ.get("NEOSIA_API_TOKEN")
    }

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

        if json_response["success"] == "0": return None
        
        user = json_response["data"]
        return user
    else:
        print(response)
        return None

def request_data_to_neosia(auth_url, parameters, headers):
    try:
        response = requests.post(auth_url, params=parameters, headers=headers)
    except MissingSchema:
        return None
    return response
