from django.conf import settings
from django.db.models import QuerySet
from learning_outcomes_assessment.utils import request_data_to_neosia
from .models import (
    KelasMataKuliahSemester,
    MataKuliahSemester,
)
from mata_kuliah_kurikulum.models import MataKuliahKurikulum


PRODI_SEMESTER_URL = 'https://customapi.neosia.unhas.ac.id/getProdiSemester'
MATA_KULIAH_SEMESTER_URL = 'https://customapi.neosia.unhas.ac.id/getKelasBySemester'
PESERTA_MATA_KULIAH_URL = 'https://customapi.neosia.unhas.ac.id/getMahasiswaByKelas'
DOSEN_MATA_KULIAH_URL = 'https://customapi.neosia.unhas.ac.id/getDosenByKelas'


def get_kelas_mk_semester(semester_prodi_id: int):
    list_kelas_mk_semester = []

    # Get MK semester
    parameters = {
        'id_prodi_semester': semester_prodi_id
    }
    json_response = request_data_to_neosia(MATA_KULIAH_SEMESTER_URL, parameters)
    if json_response is None: return list_kelas_mk_semester

    for mk_semester_per_kelas in json_response:
        mata_kuliah = {
            'id': mk_semester_per_kelas['id'],
            'id_mata_kuliah': mk_semester_per_kelas['id_mata_kuliah'],
            'nama': mk_semester_per_kelas['nama']
        }

        list_kelas_mk_semester.append(mata_kuliah)

    return list_kelas_mk_semester


def get_dosen_kelas_mk_semester(kelas_mk_semester_id: int):
    list_dosen = []
    parameters = {
        'id_kelas': kelas_mk_semester_id
    }

    json_response = request_data_to_neosia(DOSEN_MATA_KULIAH_URL, parameters)
    if json_response is None: return list_dosen

    for dosen_data in json_response:
        dosen = {
            'nip': dosen_data['nip'],
            'nama': dosen_data['nama'],
            'id_prodi': dosen_data['id_prodi']
        }

        list_dosen.append(dosen)

    return list_dosen


def get_kelas_mk_semester_choices(semester_prodi_id: int):
    """Get mata kuliah semester choices for choice field
    Returns only mata kuliah kurikulum because all classess in mata kuliah
    semester will be synchronized

    Args:
        semester_prodi_id (int): Semester Prodi ID

    Returns:
        list: List mata kuliah semester
    """
    list_kelas_mk_semester = get_kelas_mk_semester(semester_prodi_id)
    kelas_mk_semester_choices = []

    for mk_semester_per_kelas in list_kelas_mk_semester:
        id_mk_kurikulum = mk_semester_per_kelas['id_mata_kuliah']
        id_kelas_mk_semester = mk_semester_per_kelas['id']

        kelas_mk_semester_qs = KelasMataKuliahSemester.objects.filter(id_neosia=id_kelas_mk_semester)

        # If kelas MK semester is already in database, skip 
        if kelas_mk_semester_qs.exists(): continue

        # Check whether mata kuliah kurikulum exist in database
        try:
            mk_kurikulum_obj = MataKuliahKurikulum.objects.get(id_neosia=id_mk_kurikulum)
        except MataKuliahKurikulum.DoesNotExist or MataKuliahKurikulum.MultipleObjectsReturned:
            continue

        kelas_mk_semester = {
            'id_neosia': id_kelas_mk_semester,
            'kode': mk_kurikulum_obj.kode,
            'nama': mk_semester_per_kelas['nama'],
            'sks': mk_kurikulum_obj.sks,
        }

        kelas_mk_semester_choice = kelas_mk_semester['id_neosia'], kelas_mk_semester
        kelas_mk_semester_choices.append(kelas_mk_semester_choice)

    return kelas_mk_semester_choices


def get_update_kelas_mk_semester_choices(mk_semester: MataKuliahSemester):
    list_kelas_mk_semester: QuerySet[KelasMataKuliahSemester] = mk_semester.get_kelas_mk_semester()
    list_kelas_mk_semester_response = get_kelas_mk_semester(mk_semester.semester.id_neosia)
    update_kelas_mk_semester_choices = []

    for kelas_mk_semester in list_kelas_mk_semester:
        for kelas_mk_semester_response in list_kelas_mk_semester_response:
            if kelas_mk_semester.id_neosia != kelas_mk_semester_response['id']: continue

            try:
                mk_kurikulum_obj = MataKuliahKurikulum.objects.get(id_neosia=kelas_mk_semester_response['id_mata_kuliah'])
            except MataKuliahKurikulum.DoesNotExist or MataKuliahKurikulum.MultipleObjectsReturned:
                continue
            
            # Check:
            # *Kelas MK Semester > nama
            # *Kelas MK Semester > MK Semester > MK Kurikulum > id neosia
            isDataOkay = kelas_mk_semester.nama == kelas_mk_semester_response['nama']
            
            if isDataOkay: break

            # Just to show table strip in update choice field (list view model C)
            kelas_mk_semester_response.update({
                'mk_semester': {
                    'mk_kurikulum': mk_kurikulum_obj
                }
            })
            update_kelas_mk_semester_data = {
                'new': kelas_mk_semester_response,
                'old': kelas_mk_semester,
            }

            update_kelas_mk_semester_choice = kelas_mk_semester.id_neosia, update_kelas_mk_semester_data
            update_kelas_mk_semester_choices.append(update_kelas_mk_semester_choice)

            break
    
    return update_kelas_mk_semester_choices
