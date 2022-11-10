from django.conf import settings
import os
import requests


KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getKurikulum'
MATA_KULIAH_KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getMKbyKurikulumAndProdi'
ALL_SEMESTER_URL = 'https://customapi.neosia.unhas.ac.id/getAllSemester'
SEMESTER_BY_KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getSemesterByKurikulum'
DETAIL_SEMESTER_URL = 'https://customapi.neosia.unhas.ac.id/getSemesterDetail'

def request_data_to_neosia(auth_url: str, params: dict = {}, headers: dict = {}):
    headers['token'] = os.environ.get('NEOSIA_API_TOKEN')
    
    try:
        response = requests.post(auth_url, params=params, headers=headers)
    except requests.exceptions.SSLError:
        if settings.DEBUG: 
            print("SSL Error")
            response = requests.post(auth_url, params=params, headers=headers, verify=False)
    except requests.exceptions.ConnectTimeout:
        # TODO: ACTIONS ON CONNECT TIMEOUT
        if settings.DEBUG:
            print('Timeout')
            return None

    if response.status_code == 200:
        json_response = response.json()
        
        if len(json_response) == 0: 
            if settings.DEBUG: print('JSON is empty. {}'.format(response.url))
            return None

        return json_response
    else:
        if settings.DEBUG: print(response.raw)
        return None

def get_kurikulum_by_prodi(prodi_id: int):
    parameters = {
        'prodi_kode': prodi_id
    }

    json_response = request_data_to_neosia(KURIKULUM_URL, params=parameters)
    kurikulum_choices = []
    if json_response is None: return tuple(kurikulum_choices)

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

def get_mata_kuliah_kurikulum(kurikulum_id: int, prodi_id: int):
    parameters = {
        'id_prodi': prodi_id,
        'id_kurikulum': kurikulum_id
    }

    json_response = request_data_to_neosia(MATA_KULIAH_KURIKULUM_URL, params=parameters)
    list_mata_kuliah_kurikulum = []
    if json_response is None: return list_mata_kuliah_kurikulum

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
    
    return list_mata_kuliah_kurikulum

def get_all_semester():
    json_response = request_data_to_neosia(ALL_SEMESTER_URL)
    semester_choices = []
    if json_response is None: return tuple(semester_choices)

    for semester_data in json_response:
        semester_choice = {
            'id_neosia': semester_data['id'],
            'tahun_ajaran': semester_data['tahun_ajaran'],
            'jenis': semester_data['jenis'],
            'nama': 'Semester {} {}'.format(
                semester_data['tahun_ajaran'],
                semester_data['jenis'].capitalize()
            ),
        }

        # Convert it to input value, options
        semester_choice = semester_data['id'], semester_choice

        semester_choices.append(semester_choice)
    
    return tuple(semester_choices)


def get_semester_by_kurikulum(kurikulum_id: int):
    """Get semester by kurikulum

    Args:
        kurikulum_id (int): Kurikulum ID

    Returns:
        list: All semester by kurikulum ID
    """

    # Request semester by kurikulum
    parameters = {
        'id_kurikulum': kurikulum_id
    }
    # TODO: OPTIMIZE QUERY
    json_response = request_data_to_neosia(SEMESTER_BY_KURIKULUM_URL, params=parameters)
    list_semester_id = []
    semester_choices = []
    if json_response is None: return list_semester_id
    
    # Get all semester IDs
    for semester_data in json_response:
        semester_id = semester_data['id_semester']
        list_semester_id.append(semester_id)

    if len(list_semester_id) == 0: return semester_choices

    # Get all detail semester by semester ID
    for semester_id in list_semester_id:
        parameters = {
            'id_semester': semester_id
        }
        json_response = request_data_to_neosia(DETAIL_SEMESTER_URL, params=parameters)

        if json_response is None: continue

        semester_data = json_response[0]
        semester_choice = {
            'id_neosia': semester_data['id'],
            'tahun_ajaran': semester_data['tahun_ajaran'],
            'jenis': semester_data['jenis'],
            'nama': 'Semester {} {}'.format(
                semester_data['tahun_ajaran'],
                semester_data['jenis'].capitalize()
            ),
        }

        # Convert it to input value, options
        semester_choice = semester_data['id'], semester_choice
        semester_choices.append(semester_choice)
    
    return semester_choices
