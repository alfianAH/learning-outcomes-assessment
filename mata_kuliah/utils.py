from django.conf import settings
from learning_outcomes_assessment.utils import request_data_to_neosia
from .models import MataKuliahKurikulum, KelasMataKuliahSemester


DETAIL_MATA_KULIAH_URL = 'https://customapi.neosia.unhas.ac.id/getMKDetail'
MATA_KULIAH_KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getMKbyKurikulumAndProdi'

PRODI_SEMESTER_URL = 'https://customapi.neosia.unhas.ac.id/getProdiSemester'
MATA_KULIAH_SEMESTER_URL = 'https://customapi.neosia.unhas.ac.id/getKelasBySemester'
PESERTA_MATA_KULIAH_URL = 'https://customapi.neosia.unhas.ac.id/getMahasiswaByKelas'
DOSEN_MATA_KULIAH_URL = 'https://customapi.neosia.unhas.ac.id/getDosenByKelas'


def get_mk_kurikulum(kurikulum_id: int, prodi_id: int):
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
            'id_neosia': int(id_mk_kurikulum),
            'kode': mata_kuliah_data['kode'],
            'nama': mata_kuliah_data['nama_resmi'],
            'sks': sks_mk_kurikulum,
        }

        list_id_mk_kurikulum.append(id_mk_kurikulum)
        list_mata_kuliah_kurikulum.append(mata_kuliah)
    
    return list_mata_kuliah_kurikulum


def get_detail_mk(mata_kuliah_id: int):
    parameters = {
        'id_mata_kuliah': mata_kuliah_id,
    }

    json_response = request_data_to_neosia(DETAIL_MATA_KULIAH_URL, params=parameters)
    if json_response is None: return None

    detail_mata_kuliah = json_response[0]
    mata_kuliah_data = {
        'id_neosia': mata_kuliah_id,
        'prodi': detail_mata_kuliah['id_prodi'],
        'kurikulum': detail_mata_kuliah['id_kurikulum'],
        'kode': detail_mata_kuliah['kode'],
        'nama': detail_mata_kuliah['nama_resmi'],
        'sks': detail_mata_kuliah.get('sks', 0),
    }
    
    return mata_kuliah_data


def get_mk_kurikulum_choices(kurikulum_id: int, prodi_id: int):
    list_mk_kurikulum = get_mk_kurikulum(kurikulum_id, prodi_id)
    mk_kurikulum_choices = []

    for mk_kurikulum_data in list_mk_kurikulum:
        mk_kurikulum_id = mk_kurikulum_data['id_neosia']
        # Search in database
        object_in_db = MataKuliahKurikulum.objects.filter(id_neosia=mk_kurikulum_id)
        if object_in_db.exists(): continue

        mk_kurikulum_choice = mk_kurikulum_data['id_neosia'], mk_kurikulum_data
        mk_kurikulum_choices.append(mk_kurikulum_choice)
    
    return mk_kurikulum_choices


def get_update_mk_kurikulum_choices(kurikulum_id: int, prodi_id: int):
    json_response = get_mk_kurikulum(kurikulum_id, prodi_id)
    update_mk_kurikulum_choices = []

    for mk_kurikulum_data in json_response:
        id_mk_kurikulum = mk_kurikulum_data['id_neosia']

        try:
            mk_kurikulum_obj = MataKuliahKurikulum.objects.get(id_neosia=id_mk_kurikulum)
        except MataKuliahKurikulum.DoesNotExist:
            continue
        except MataKuliahKurikulum.MultipleObjectsReturned:
            if settings.DEBUG: print('Kurikulum object returns multiple objects. ID: {}'.format(id_mk_kurikulum))
            continue
        
        isDataOkay = mk_kurikulum_obj.nama == mk_kurikulum_data['nama'] and mk_kurikulum_obj.sks == mk_kurikulum_data['sks'] and mk_kurikulum_obj.kode == mk_kurikulum_data['kode']

        if isDataOkay: continue

        update_mk_kurikulum_data = {
            'new': mk_kurikulum_data,
            'old': mk_kurikulum_obj,
        }
        update_mk_kurikulum_choice = id_mk_kurikulum, update_mk_kurikulum_data
        update_mk_kurikulum_choices.append(update_mk_kurikulum_choice)

    return update_mk_kurikulum_choices


def get_mk_semester(semester_prodi_id: int):
    list_mata_kuliah_semester = []

    # Get MK semester
    parameters = {
        'id_prodi_semester': semester_prodi_id
    }
    json_response = request_data_to_neosia(MATA_KULIAH_SEMESTER_URL, parameters)
    if json_response is None: return list_mata_kuliah_semester

    for mk_semester_per_kelas in json_response:
        mata_kuliah = {
            'id': mk_semester_per_kelas['id'],
            'id_mata_kuliah': mk_semester_per_kelas['id_mata_kuliah'],
            'nama': mk_semester_per_kelas['nama']
        }

        list_mata_kuliah_semester.append(mata_kuliah)

    return list_mata_kuliah_semester


def get_mk_semester_choices(semester_id: int):
    """Get mata kuliah semester choices for choice field
    Returns only mata kuliah kurikulum because all classess in mata kuliah
    semester will be synchronized

    Args:
        semester_id (int): Semester ID

    Returns:
        list: List mata kuliah semester
    """
    list_mk_semester = get_mk_semester(semester_id)
    list_id_mk_kurikulum = []
    mk_semester_choices = []

    for mk_semester_per_kelas in list_mk_semester:
        id_mk_kurikulum = mk_semester_per_kelas['id_mata_kuliah']
        id_kelas_mk_semester = mk_semester_per_kelas['id_neosia']

        if settings.DEBUG: 
            print('Semester: {}'.format(mk_semester_per_kelas['nama']))
        kelas_mk_semester_qs = KelasMataKuliahSemester.objects.filter(id_neosia=id_kelas_mk_semester)

        # If kelas MK semester is already in database, skip 
        if kelas_mk_semester_qs.exists(): continue

        if id_mk_kurikulum in list_id_mk_kurikulum: continue

        # Check whether mata kuliah kurikulum exist in database
        try:
            mk_kurikulum_obj = MataKuliahKurikulum.objects.get(id_neosia=id_mk_kurikulum)
        except MataKuliahKurikulum.DoesNotExist or MataKuliahKurikulum.MultipleObjectsReturned:
            continue
        
        if settings.DEBUG:
            print('Kurikulum: {} - {}'.format(mk_kurikulum_obj.nama, mk_kurikulum_obj.kode))

        mata_kuliah = {
            'id_neosia': mk_kurikulum_obj.id_neosia,
            'kode': mk_kurikulum_obj.kode,
            'nama': mk_kurikulum_obj.nama,
            'sks': mk_kurikulum_obj.sks,
        }
        list_id_mk_kurikulum.append(id_mk_kurikulum)

        mk_semester_choice = mata_kuliah['id_neosia'], mata_kuliah
        mk_semester_choices.append(mk_semester_choice)

    return mk_semester_choices
