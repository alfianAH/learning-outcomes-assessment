from django.conf import settings
from learning_outcomes_assessment.utils import request_data_to_neosia
from .models import Semester, SemesterKurikulum


SEMESTER_BY_KURIKULUM_URL = 'https://customapi.neosia.unhas.ac.id/getSemesterByKurikulum'
DETAIL_SEMESTER_URL = 'https://customapi.neosia.unhas.ac.id/getSemesterDetail'


def get_semester_by_kurikulum(kurikulum_id: int):
    """Get semesters by kurikulum

    Args:
        kurikulum_id (int): Kurikulum ID

    Returns:
        list: All semesters by kurikulum
    """

    # Request semester by kurikulum
    parameters = {
        'id_kurikulum': kurikulum_id
    }
    json_response = request_data_to_neosia(SEMESTER_BY_KURIKULUM_URL, params=parameters)
    list_semester = []
    if json_response is None: return list_semester
    
    # Get all semester
    for semester_data in json_response:
        semester = {
            'id_neosia': semester_data['id_semester'],
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


def get_semester_by_kurikulum_choices(kurikulum_id: int):
    """Get semester by kurikulum choices

    Args:
        kurikulum_id (int): Kurikulum ID

    Returns:
        list: All semester by kurikulum ID with detail semester
    """

    # Request semester by kurikulum
    list_semester = get_semester_by_kurikulum(kurikulum_id)
    semester_choices = []

    # Get all detail semester by semester ID
    for semester_data in list_semester:
        semester_id = semester_data['id_neosia']
        # Search in database
        object_in_db = SemesterKurikulum.objects.filter(kurikulum=kurikulum_id, semester=int(semester_id))
        if object_in_db.exists(): continue

        # Convert it to input value, options
        semester_choice = semester_data['id_neosia'], semester_data
        semester_choices.append(semester_choice)
    
    return semester_choices


def get_update_semester_choices(kurikulum_id: int):
    # Request semester by kurikulum
    json_response = get_semester_by_kurikulum(kurikulum_id)
    update_semester_choices = []

    for semester_data in json_response:
        id_semester = semester_data['id_neosia']

        try:
            semester_obj = Semester.objects.get(id_neosia=id_semester)
        except Semester.DoesNotExist:
            continue
        except Semester.MultipleObjectsReturned:
            if settings.DEBUG: print('Semester object returns multiple objects. ID: {}'.format(id_semester))
            continue
        
        # Filter if semester is in semester kurikulum
        try:
            SemesterKurikulum.objects.get(semester=id_semester, kurikulum=kurikulum_id)
        except SemesterKurikulum.DoesNotExist:
            continue
        except SemesterKurikulum.MultipleObjectsReturned:
            if settings.DEBUG: print('Semester Kurikulum object returns multiple objects. Kurikulum ID: {}, Semester Id: {}'.format(kurikulum_id, id_semester))
            continue

        isDataOkay = semester_obj.nama == semester_data['nama'] and str(semester_obj.tahun_ajaran) == semester_data['tahun_ajaran'] and semester_obj.get_tipe_semester_display().lower() == semester_data['tipe_semester'].lower()

        if isDataOkay: continue

        update_semester_data = {
            'new': semester_data,
            'old': semester_obj,
        }

        update_semester_choice = id_semester, update_semester_data
        update_semester_choices.append(update_semester_choice)

    return update_semester_choices
