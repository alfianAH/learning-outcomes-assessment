from django.conf import settings
import os
import requests


KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getKurikulum'


def get_kurikulum_by_prodi(prodi_id):
    parameters = {
        'prodi_kode': prodi_id
    }
    headers = {
        "token": os.environ.get("NEOSIA_API_TOKEN")
    }

    response = requests.post(KURIKULUM_URL, params=parameters, headers=headers)

    if response.status_code == 200:
        json_response = response.json()
        
        if len(json_response) == 0: return None
        
        return json_response
    else: 
        if settings.DEBUG: print(response)
        return None
