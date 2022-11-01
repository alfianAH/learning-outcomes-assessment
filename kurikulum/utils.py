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

        kurikulum_choices = []

        for kurikulum_data in json_response:
            kurikulum_choice = {
                'id_neosia': kurikulum_data['id'],
                'prodi': kurikulum_data['id_prodi'],
                'nama': kurikulum_data['nama'],
                'tahun_mulai': kurikulum_data['tahun'],
                'is_active': kurikulum_data['is_current'] == 1,
            }
            kurikulum_choice = kurikulum_data['id'], kurikulum_choice

            kurikulum_choices.append(kurikulum_choice)
        
        return tuple(kurikulum_choices)
    else: 
        if settings.DEBUG: print(response)
        return None
