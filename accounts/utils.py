import os
from django.conf import settings
from django.urls import reverse
import requests
from learning_outcomes_assessment.utils import request_data_to_neosia
from requests import Request, Session
from requests.exceptions import MissingSchema, SSLError
from .models import ProgramStudi, ProgramStudiJenjang
from .enums import RoleChoices


ALL_PRODI_URL = 'https://customapi.neosia.unhas.ac.id/getAllProdi'
DETAIL_JENJANG_STUDI_URL = 'https://customapi.neosia.unhas.ac.id/getDetilProdiJenjang'
DETAIL_FAKULTAS_URL = 'https://customapi.neosia.unhas.ac.id/getDetilFakultas'

MBERKAS_OAUTH_TOKEN_URL = 'https://mberkas.unhas.ac.id/oauth/token'
MBERKAS_OAUTH_BEARER = 'https://mberkas.unhas.ac.id/api/checkStatus'

MHS_AUTH_URL = 'https://customapi.neosia.unhas.ac.id/checkMahasiswa2'

MHS_PROFILE_URL = 'https://customapi.neosia.unhas.ac.id/GetProfilMhs'
DOSEN_PROFILE_URL = 'https://customapi.neosia.unhas.ac.id/getDetilDosen'


def get_user_profile(user: dict, role: str):
    """Get user's profile

    Args:
        user (str): User's data
        role (str): User's role

    Returns:
        dict: JSON response from Neosia API
    """

    # Request authenticated user's profile
    match(role):
        case RoleChoices.DOSEN:
            parameters = {
                'nip': user
            }
            json_response = request_data_to_neosia(DOSEN_PROFILE_URL, params=parameters)
            if json_response is None: return None

            user_profile = json_response[0]
            return user_profile
        case RoleChoices.MAHASISWA:
            parameters = {
                'nim': user
            }
            json_response = request_data_to_neosia(MHS_PROFILE_URL, parameters)
    
            if json_response is None: return None

            # Return None if the request has no data
            if len(json_response['data']) == 0: return None
            
            user_profile = json_response['data'][0]
            return user_profile


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

    try:
        response = requests.get(MBERKAS_OAUTH_BEARER, headers={
            'Authorization': 'Bearer {}'.format(access_token)
        })
    except SSLError:
        if settings.DEBUG: print('SSL Error')
        response = requests.get(MBERKAS_OAUTH_BEARER, verify=False, headers={
            'Authorization': 'Bearer {}'.format(access_token)
        })

    if response.status_code == 200:
        user = response.json()
        return user
    else:
        if settings.DEBUG: print(response.raw)
        return None


def validate_mahasiswa(username: str, password: str):
    parameters = {
        'username': username,
        'password': password
    }
    headers = {
        'token': os.environ.get('NEOSIA_API_TOKEN')
    }

    json_response = request_data_to_neosia(MHS_AUTH_URL, parameters, headers)

    if json_response is None: return None

    # Return None if the request is not success
    if json_response['success'] == '0': return None
    
    user = json_response['data']
    return user


def get_detail_jenjang_studi(jenjang_studi_id: int):
    parameters = {
        'id': jenjang_studi_id
    }
    json_response = request_data_to_neosia(DETAIL_JENJANG_STUDI_URL, params=parameters)
    if json_response is None: return None
    detail_jenjang_studi = json_response[0]

    jenjang_studi_data = {
        'id_neosia': detail_jenjang_studi['id'],
        'nama': detail_jenjang_studi['nama'],
        'kode': detail_jenjang_studi['kode']
    }

    return jenjang_studi_data


def get_detail_fakultas(fakultas_id: int):
    parameters = {
        'id': fakultas_id
    }
    json_response = request_data_to_neosia(DETAIL_FAKULTAS_URL, params=parameters)
    if json_response is None: return None
    detail_fakultas = json_response[0]

    fakultas_data = {
        'id_neosia': detail_fakultas['id'],
        'nama': detail_fakultas['nama_resmi']
    }
    return fakultas_data


def get_all_prodi():
    json_response = request_data_to_neosia(ALL_PRODI_URL)
    list_prodi = []
    list_jenjang_studi = {}
    list_fakultas = {}
    if json_response is None: return list_prodi

    for data_prodi in json_response:
        if data_prodi['is_active'] == 0: continue

        # Get jenjang studi
        jenjang_studi_id = data_prodi['id_prodi_jenjang']

        if jenjang_studi_id not in list_jenjang_studi.keys():
            jenjang_studi = get_detail_jenjang_studi(jenjang_studi_id)
            list_jenjang_studi[jenjang_studi_id] = jenjang_studi

        # Get fakultas
        fakultas_id = data_prodi['id_fakultas']
        if fakultas_id not in list_fakultas.keys():
            fakultas = get_detail_fakultas(fakultas_id)
            list_fakultas[fakultas_id] = fakultas

        prodi = {
            'id_neosia': data_prodi['id'],
            'nama': data_prodi['nama_resmi'],
            'jenjang_studi': list_jenjang_studi[jenjang_studi_id],
            'fakultas': list_fakultas[fakultas_id],
        }

        list_prodi.append(prodi)

    return list_prodi


def get_all_prodi_choices():
    list_prodi = get_all_prodi()
    list_prodi_choices = []

    for prodi in list_prodi:
        prodi_jenjang_qs = ProgramStudiJenjang.objects.filter(
            id_neosia=prodi['id_neosia']
        )
        if prodi_jenjang_qs.exists(): continue

        prodi_choice = prodi['id_neosia'], prodi

        list_prodi_choices.append(prodi_choice)

    return list_prodi_choices


def get_update_prodi_jenjang_choices(list_prodi_id: list[int]):
    list_prodi = get_all_prodi()
    update_prodi_jenjang_choices = []

    for prodi in list_prodi:
        if prodi['id_neosia'] not in list_prodi_id: continue

        try:
            prodi_jenjang_obj = ProgramStudiJenjang.objects.get(id_neosia=prodi['id_neosia'])
        except ProgramStudiJenjang.DoesNotExist:
            continue
        except ProgramStudiJenjang.MultipleObjectsReturned:
            if settings.DEBUG: print('Program Studi Jenjang object returns multiple objects. ID: {}'.format(prodi['id_neosia']))
            continue
        
        isDataOkay = prodi_jenjang_obj.nama == prodi['nama'] and prodi_jenjang_obj.jenjang_studi.nama == prodi['jenjang_studi']['nama'] and prodi_jenjang_obj.jenjang_studi.kode == prodi['jenjang_studi']['kode']

        if isDataOkay: continue

        update_prodi_jenjang_data = {
            'new': prodi,
            'old': prodi_jenjang_obj,
        }
        update_prodi_jenjang_choice = prodi['id_neosia'], update_prodi_jenjang_data
        update_prodi_jenjang_choices.append(update_prodi_jenjang_choice)

    return update_prodi_jenjang_choices


def get_prodi_jenjang_db_choices(program_studi: ProgramStudi):
    """Get program studi jenjang choices by program studi obj in database

    Args:
        program_studi (ProgramStudi): Program Studi object

    Returns:
        list: program studi jenjang choices (id, nama)
    """
    prodi_jenjang_qs = ProgramStudiJenjang.objects.filter(
        program_studi=program_studi
    )
    prodi_jenjang_choices = []

    for prodi_jenjang in prodi_jenjang_qs:
        prodi_jenjang_choice = prodi_jenjang.id_neosia, prodi_jenjang.nama
        prodi_jenjang_choices.append(prodi_jenjang_choice)

    return prodi_jenjang_choices
