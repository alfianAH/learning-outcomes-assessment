from django.conf import settings
import os
import requests


KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getKurikulum'
MATA_KULIAH_KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getMKbyKurikulumAndProdi'


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
        
        if len(json_response) == 0: 
            if settings.DEBUG: print('JSON is empty')
            return None

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

def get_mata_kuliah_kurikulum(kurikulum_id, prodi_id):
    parameters = {
        'id_prodi': prodi_id,
        'id_kurikulum': kurikulum_id
    }
    headers = {
        "token": os.environ.get("NEOSIA_API_TOKEN")
    }

    response = requests.post(MATA_KULIAH_KURIKULUM_URL, params=parameters, headers=headers)

    if response.status_code == 200:
        json_response = response.json()
        
        if len(json_response) == 0: 
            if settings.DEBUG: print('JSON is empty')
            return None

        list_mata_kuliah_kurikulum = []

        for mata_kuliah_data in json_response:
            mata_kuliah = {
                'prodi': mata_kuliah_data['id_prodi'],
                'kurikulum': mata_kuliah_data['id_kurikulum'],
                'id': mata_kuliah_data['id'],
                'kode_mk': mata_kuliah_data['kode'],
                'nama': mata_kuliah_data['nama_resmi'],
                'sks': mata_kuliah_data['jumlah_sks']
            }

            list_mata_kuliah_kurikulum.append(mata_kuliah)
        
        print(list_mata_kuliah_kurikulum)
        return list_mata_kuliah_kurikulum
    else: 
        if settings.DEBUG: print(response)
        return None
