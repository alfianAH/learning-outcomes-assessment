import os
import requests


AUTH_URL = "https://customapi.neosia.unhas.ac.id/checkMahasiswa2"

def validate_user(username: str, password: str):
    parameters = {
        "username": username,
        "password": password
    }
    headers = {
        "token": os.environ.get("NEOSIA_API_TOKEN")
    }
    response = requests.post(AUTH_URL, params=parameters, headers=headers)

    if response.status_code == 200:
        json_response = response.json()

        if json_response["success"] == "0": return None
        
        user = json_response["data"]
        return user
    else:
        print(response)
        return None