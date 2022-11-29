from django.conf import settings
from .models import Kurikulum
from learning_outcomes_assessment.utils import request_data_to_neosia


KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getKurikulum'
DETAIL_KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getKurikulumDetail'
MATA_KULIAH_KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getMKbyKurikulumAndProdi'


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
    list_id_mk_kurikulum = []
    if json_response is None: return list_mata_kuliah_kurikulum

    for mata_kuliah_data in json_response:
        id_mk_kurikulum = mata_kuliah_data['id_mata_kuliah']
        sks_mk_kurikulum = mata_kuliah_data['jumlah_sks']

        # Add all SKS to existing MK Kurikulum
        if id_mk_kurikulum in list_id_mk_kurikulum:
            for mk_kurikulum in list_mata_kuliah_kurikulum:
                if mk_kurikulum['id_neosia'] != id_mk_kurikulum: continue
                mk_kurikulum['sks'] += sks_mk_kurikulum
            continue

        mata_kuliah = {
            'prodi': mata_kuliah_data['id_prodi'],
            'kurikulum': mata_kuliah_data['id_kurikulum'],
            'id_neosia': id_mk_kurikulum,
            'kode': mata_kuliah_data['kode'],
            'nama': mata_kuliah_data['nama_resmi'],
            'sks': sks_mk_kurikulum,
        }

        list_id_mk_kurikulum.append(id_mk_kurikulum)
        list_mata_kuliah_kurikulum.append(mata_kuliah)
    
    return list_mata_kuliah_kurikulum


def get_kurikulum_by_prodi_choices(prodi_id: int):
    json_response = get_kurikulum_by_prodi(prodi_id)
    kurikulum_choices = []

    for kurikulum_data in json_response:
        kurikulum_choice = kurikulum_data['id_neosia'], kurikulum_data
        kurikulum_choices.append(kurikulum_choice)
    
    return kurikulum_choices


def get_update_kurikulum_choices(prodi_id: int):
    json_response = get_kurikulum_by_prodi(prodi_id)
    update_kurikulum_choices = []

    for kurikulum_data in json_response:
        id_kurikulum = kurikulum_data['id_neosia']

        try:
            kurikulum_obj = Kurikulum.objects.get(id_neosia=id_kurikulum)
        except Kurikulum.DoesNotExist:
            continue
        except Kurikulum.MultipleObjectsReturned:
            if settings.DEBUG: print('Kurikulum object returns multiple objects. ID: {}'.format(id_kurikulum))
            continue
        
        isDataOkay = kurikulum_obj.id_neosia == id_kurikulum and kurikulum_obj.nama == kurikulum_data['nama'] and kurikulum_obj.is_active == kurikulum_data['is_active'] and kurikulum_obj.tahun_mulai == kurikulum_data['tahun_mulai']

        if isDataOkay: continue

        update_kurikulum_data = {
            'new': kurikulum_data,
            'old': kurikulum_obj,
        }
        update_kurikulum_choice = id_kurikulum, update_kurikulum_data
        update_kurikulum_choices.append(update_kurikulum_choice)

    return update_kurikulum_choices
