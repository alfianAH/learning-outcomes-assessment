import os
import requests

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
            response = requests.post(ADMIN_AUTH_URL, params=parameters, headers=headers)
        case RoleChoices.DOSEN:
            response = requests.post(DOSEN_AUTH_URL, params=parameters, headers=headers)
        case RoleChoices.MAHASISWA:
            response = requests.post(MHS_AUTH_URL, params=parameters, headers=headers)

    if response.status_code == 200:
        json_response = response.json()

        if json_response["success"] == "0": return None
        
        user = json_response["data"]
        return user
    else:
        print(response)
        return None
