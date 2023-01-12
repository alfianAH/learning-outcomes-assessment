from django.conf import settings
from learning_outcomes_assessment.utils import request_data_to_neosia
from .models import Semester, SemesterProdi


ALL_SEMESTER_URL = 'https://customapi.neosia.unhas.ac.id/getAllSemester'
SEMESTER_PRODI_URL = 'https://customapi.neosia.unhas.ac.id/getProdiSemester'
DETAIL_SEMESTER_URL = 'https://customapi.neosia.unhas.ac.id/getSemesterDetail'


def get_all_semester():
    json_response = request_data_to_neosia(ALL_SEMESTER_URL)
    list_semester = []
    if json_response is None: return list_semester

    for semester_data in json_response:
        semester = {
            'id_neosia': semester_data['id'],
            'tahun_ajaran': semester_data['tahun_ajaran'],
            'tipe_semester': semester_data['jenis'],
            'nama': 'Semester {} {}'.format(
                semester_data['tahun_ajaran'],
                semester_data['jenis'].capitalize()
            ),
        }

        list_semester.append(semester)

    return list_semester


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


def get_semester_prodi(prodi_jenjang_id: int):
    """Get semesters by prodi

    Args:
        prodi_jenjang_id (int): Program Studi Jenjang ID

    Returns:
        list: All semester prodi
    """

    # Request semester prodi
    parameters = {
        'prodi_kode': prodi_jenjang_id
    }
    json_response = request_data_to_neosia(SEMESTER_PRODI_URL, params=parameters)
    list_semester_prodi = []
    if json_response is None: return list_semester_prodi
    
    all_semester = get_all_semester()

    # Get all semester
    for semester_prodi_data in json_response:
        id_semester = semester_prodi_data['id_semester']
        
        for semester in all_semester:
            if semester['id_neosia'] != id_semester: continue
            
            # Get detail semester
            detail_semester = semester
            break
        
        if detail_semester is None: continue

        semester_prodi = {
            'id_neosia': semester_prodi_data['id'],
            'id_semester': id_semester,
            'tahun_ajaran': detail_semester['tahun_ajaran'],
            'tipe_semester': detail_semester['tipe_semester'],
            'nama': 'Semester {} {}'.format(
                detail_semester['tahun_ajaran'],
                detail_semester['tipe_semester'].capitalize()
            ),
        }
        list_semester_prodi.append(semester_prodi)
    return list_semester_prodi


def get_semester_prodi_choices(prodi_jenjang_id: int):
    """Get semester by prodi choices

    Args:
        prodi_id (int): Program Studi Jenjang ID

    Returns:
        list: All semester by prodi ID with detail semester
    """

    # Request semester by kurikulum
    list_semester_prodi = get_semester_prodi(prodi_jenjang_id)
    semester_choices = []

    # Get all detail semester by semester ID
    for semester_prodi_data in list_semester_prodi:
        semester_id = semester_prodi_data['id_neosia']
        # Search in database
        object_in_db = SemesterProdi.objects.filter(
            tahun_ajaran_prodi__prodi_jenjang__id_neosia=prodi_jenjang_id, 
            semester=int(semester_id)
        )
        if object_in_db.exists(): continue

        # Convert it to input value, options
        semester_choice = semester_prodi_data['id_neosia'], semester_prodi_data
        semester_choices.append(semester_choice)
    
    semester_choices.sort(reverse=True)
    return semester_choices


def get_update_semester_prodi_choices(prodi_jenjang_id: int):
    # Request semester by kurikulum
    json_response = get_semester_prodi(prodi_jenjang_id)
    update_semester_choices = []

    for semester_prodi_data in json_response:
        id_semester_prodi = semester_prodi_data['id_neosia']

        try:
            semester_prodi_obj = SemesterProdi.objects.get(id_neosia=id_semester_prodi)
        except Semester.DoesNotExist:
            continue
        except Semester.MultipleObjectsReturned:
            if settings.DEBUG: print('Semester Prodi object returns multiple objects. ID: {}'.format(id_semester_prodi))
            continue

        isDataOkay = semester_prodi_obj.semester.nama == semester_prodi_data['nama'] and str(semester_prodi_obj.semester.tahun_ajaran) == semester_prodi_data['tahun_ajaran'] and semester_prodi_obj.semester.get_tipe_semester_display().lower() == semester_prodi_data['tipe_semester'].lower()

        if isDataOkay: continue

        update_semester_data = {
            'new': semester_prodi_data,
            'old': semester_prodi_obj,
        }

        update_semester_choice = id_semester_prodi, update_semester_data
        update_semester_choices.append(update_semester_choice)

    return update_semester_choices
