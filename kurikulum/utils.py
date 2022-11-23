from django.conf import settings
from .models import Kurikulum
from semester.models import Semester, SemesterKurikulum
import os
import requests


KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getKurikulum'
DETAIL_KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getKurikulumDetail'
MATA_KULIAH_KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getMKbyKurikulumAndProdi'
ALL_SEMESTER_URL = 'https://customapi.neosia.unhas.ac.id/getAllSemester'
SEMESTER_BY_KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getSemesterByKurikulum'
DETAIL_SEMESTER_URL = 'https://customapi.neosia.unhas.ac.id/getSemesterDetail'

def request_data_to_neosia(auth_url: str, params: dict = {}, headers: dict = {}):
    headers['token'] = os.environ.get('NEOSIA_API_TOKEN')
    
    try:
        response = requests.post(auth_url, params=params, headers=headers)
    except requests.exceptions.SSLError:
        if settings.DEBUG: print("SSL Error")
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
    list_kurikulum = []
    if json_response is None: return list_kurikulum

    for kurikulum_data in json_response:
        kurikulum = {
            'id_neosia': kurikulum_data['id'],
            'prodi': kurikulum_data['id_prodi'],
            'nama': kurikulum_data['nama'],
            'tahun_mulai': kurikulum_data['tahun'],
            'is_active': kurikulum_data['is_current'] == 1,
        }

        list_kurikulum.append(kurikulum)
    return list_kurikulum


def get_detail_kurikulum(kurikulum_id: int):
    parameters = {
        'id_kurikulum': kurikulum_id
    }

    json_response = request_data_to_neosia(DETAIL_KURIKULUM_URL, params=parameters)
    if json_response is None: return None
    kurikulum_detail = json_response[0]

    kurikulum_data = {
        'id_neosia': kurikulum_detail['id'],
        'prodi': kurikulum_detail['id_prodi'],
        'nama': kurikulum_detail['nama'],
        'tahun_mulai': kurikulum_detail['tahun'],
        'is_active': kurikulum_detail['is_current'] == 1,
    }

    return kurikulum_data


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
            'id_neosia': mata_kuliah_data['id'],
            'kode': mata_kuliah_data['kode'],
            'nama': mata_kuliah_data['nama_resmi'],
            'sks': mata_kuliah_data['jumlah_sks']
        }

        list_mata_kuliah_kurikulum.append(mata_kuliah)
    
    return list_mata_kuliah_kurikulum


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
    if json_response is None: return list_semester_id
    
    # Get all semester IDs
    for semester_data in json_response:
        semester_id = semester_data['id_semester']
        list_semester_id.append(semester_id)
    return list_semester_id


def get_detail_semester(semester_id: int):
    """Get detail semester

    Args:
        semester_id (int): Semester ID

    Returns:
        dict: Semester detail
    """

    parameters = {
        'id_semester': semester_id
    }
    json_response = request_data_to_neosia(DETAIL_SEMESTER_URL, params=parameters)

    if json_response is None: return None

    semester_data = json_response[0]
    semester_detail = {
        'id_neosia': semester_data['id'],
        'tahun_ajaran': semester_data['tahun_ajaran'],
        'tipe_semester': semester_data['jenis'],
        'nama': 'Semester {} {}'.format(
            semester_data['tahun_ajaran'],
            semester_data['jenis'].capitalize()
        ),
    }

    return semester_detail


def get_kurikulum_by_prodi_choices(prodi_id: int):
    json_response = get_kurikulum_by_prodi(prodi_id)
    kurikulum_choices = []

    for kurikulum_data in json_response:
        id_kurikulum = kurikulum_data['id_neosia']
        id_prodi = kurikulum_data['prodi']

        mk_kurikulum_response = get_mata_kuliah_kurikulum(id_kurikulum, id_prodi)
        semester_by_kurikulum_response = get_semester_by_kurikulum(id_kurikulum)
        
        if len(mk_kurikulum_response) == 0 and len(semester_by_kurikulum_response) == 0: continue
        
        # Search in database
        is_all_semester_sync = True
        for semester_id in semester_by_kurikulum_response:
            semester_in_db = Semester.objects.filter(id_neosia=int(semester_id))
            if semester_in_db.exists(): continue
            # Break and set to False if kurikulum has one or more semester to sync
            is_all_semester_sync = False
            break
        
        # If all semester is already synchronized, continue
        if is_all_semester_sync: continue
        
        kurikulum_choice = kurikulum_data['id_neosia'], kurikulum_data
        kurikulum_choices.append(kurikulum_choice)
    
    return tuple(kurikulum_choices)


def get_semester_by_kurikulum_choices(kurikulum_id: int):
    """Get semester by kurikulum choices

    Args:
        kurikulum_id (int): Kurikulum ID

    Returns:
        list: All semester by kurikulum ID with detail semester
    """

    # Request semester by kurikulum
    list_semester_id = get_semester_by_kurikulum(kurikulum_id)
    new_list_semester_id = []
    for semester_id in list_semester_id:
        # Search in database
        object_in_db = SemesterKurikulum.objects.filter(semester=int(semester_id))
        if object_in_db.exists(): continue

        new_list_semester_id.append(semester_id)

    semester_choices = []
    if len(new_list_semester_id) == 0: return semester_choices

    # Get all detail semester by semester ID
    for semester_id in new_list_semester_id:
        semester_choice = get_detail_semester(semester_id)
        if semester_choice is None: continue

        # Convert it to input value, options
        semester_choice = semester_choice['id_neosia'], semester_choice
        semester_choices.append(semester_choice)
    
    return semester_choices
