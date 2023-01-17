from django.conf import settings
from django.db.models import QuerySet
from .models import Kurikulum
from accounts.models import ProgramStudi, ProgramStudiJenjang
from learning_outcomes_assessment.utils import request_data_to_neosia


KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getKurikulum'
DETAIL_KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getKurikulumDetail'


def get_kurikulum_by_prodi_jenjang(prodi_jenjang_id: int):
    parameters = {
        'prodi_kode': prodi_jenjang_id
    }

    json_response = request_data_to_neosia(KURIKULUM_URL, params=parameters)
    list_kurikulum = []
    if json_response is None: return list_kurikulum

    prodi_jenjang_obj = None
    try:
        prodi_jenjang_obj = ProgramStudiJenjang.objects.get(id_neosia=prodi_jenjang_id)
    except ProgramStudiJenjang.DoesNotExist:
        if settings.DEBUG:
            print('Cannot get prodi jenjang with ID: {}'.format(prodi_jenjang_id))
    except ProgramStudiJenjang.MultipleObjectsReturned:
        if settings.DEBUG:
            print('Prodi jenjang returns multiple objects')

    if prodi_jenjang_obj is None: return list_kurikulum

    for kurikulum_data in json_response:
        kurikulum = {
            'id_neosia': kurikulum_data['id'],
            'prodi_jenjang': prodi_jenjang_obj,
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
        'prodi_jenjang': kurikulum_detail['id_prodi'],
        'nama': kurikulum_detail['nama'],
        'tahun_mulai': kurikulum_detail['tahun'],
        'is_active': kurikulum_detail['is_current'] == 1,
    }

    return kurikulum_data


def get_kurikulum_by_prodi_jenjang_choices(prodi_jenjang_id: int):
    json_response = get_kurikulum_by_prodi_jenjang(prodi_jenjang_id)
    kurikulum_choices = []

    for kurikulum_data in json_response:
        kurikulum_choice = kurikulum_data['id_neosia'], kurikulum_data
        kurikulum_choices.append(kurikulum_choice)
    
    return kurikulum_choices


def get_update_kurikulum_choices(prodi: ProgramStudi):
    list_prodi_jenjang: QuerySet[ProgramStudiJenjang] = prodi.get_prodi_jenjang()
    update_kurikulum_choices = []

    for prodi_jenjang in list_prodi_jenjang:
        json_response = get_kurikulum_by_prodi_jenjang(prodi_jenjang.id_neosia)

        for kurikulum_data in json_response:
            id_kurikulum = kurikulum_data['id_neosia']

            try:
                kurikulum_obj = Kurikulum.objects.get(id_neosia=id_kurikulum)
            except Kurikulum.DoesNotExist:
                continue
            except Kurikulum.MultipleObjectsReturned:
                if settings.DEBUG: print('Kurikulum object returns multiple objects. ID: {}'.format(id_kurikulum))
                continue
            
            # Check:
            # *Kurikulum > nama
            # *Kurikulum > is active
            # *Kurikulum > tahun mulai
            isDataOkay = kurikulum_obj.nama == kurikulum_data['nama'] and kurikulum_obj.is_active == kurikulum_data['is_active'] and kurikulum_obj.tahun_mulai == kurikulum_data['tahun_mulai']

            if isDataOkay: continue

            update_kurikulum_data = {
                'new': kurikulum_data,
                'old': kurikulum_obj,
            }
            update_kurikulum_choice = id_kurikulum, update_kurikulum_data
            update_kurikulum_choices.append(update_kurikulum_choice)

    return update_kurikulum_choices
