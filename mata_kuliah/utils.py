from django.conf import settings
from learning_outcomes_assessment.utils import request_data_to_neosia
from .models import KelasMataKuliahSemester
from mata_kuliah_kurikulum.models import MataKuliahKurikulum


PRODI_SEMESTER_URL = 'https://customapi.neosia.unhas.ac.id/getProdiSemester'
MATA_KULIAH_SEMESTER_URL = 'https://customapi.neosia.unhas.ac.id/getKelasBySemester'
PESERTA_MATA_KULIAH_URL = 'https://customapi.neosia.unhas.ac.id/getMahasiswaByKelas'
DOSEN_MATA_KULIAH_URL = 'https://customapi.neosia.unhas.ac.id/getDosenByKelas'


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
