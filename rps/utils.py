from django.conf import settings
from django.db.models import QuerySet
from learning_outcomes_assessment.utils import clone_object
from mata_kuliah_semester.models import MataKuliahSemester
from rps.models import (
    RencanaPembelajaranSemester,
    PengembangRPS,
    KoordinatorRPS,
    DosenPengampuRPS,
    MataKuliahSyaratRPS,
    PertemuanRPS,
    RincianPertemuanRPS,
    PembelajaranPertemuanRPS,
    DurasiPertemuanRPS,
)
from semester.models import SemesterProdi


def get_semester_choices_rincian_rps_duplicate(mk_semester: MataKuliahSemester):
    # Get All MK Semester in same kurikulum
    list_mk_semester: QuerySet[MataKuliahSemester] = mk_semester.mk_kurikulum.get_mk_semester()
    semester_choices = []

    for mk_semester_obj in list_mk_semester:
        # Skip the same semester
        if mk_semester_obj.pk is mk_semester.pk: continue
        
        # Skip if MK doesn't have RPS
        if not hasattr(mk_semester_obj, 'rencanapembelajaransemester'): continue

        semester_choice = mk_semester_obj.semester.id_neosia, '{}. <a href="{}" target="_blank">Lihat RPS di sini</a>'.format(mk_semester_obj.semester.semester.nama, mk_semester_obj.get_rps_home_url())

        semester_choices.append(semester_choice)
    
    return semester_choices


def duplicate_rincian_rps(semester_prodi_id, new_mk_semester: MataKuliahSemester):
    is_success = False
    message = ''

    try:
        semester_prodi_obj = SemesterProdi.objects.get(id_neosia=semester_prodi_id)
    except (SemesterProdi.DoesNotExist, SemesterProdi.MultipleObjectsReturned):
        message = 'Semester Prodi tidak dapat ditemukan. ID: {}'.format(semester_prodi_id)
        if settings.DEBUG: print(message) 
        return (is_success, message) 
    
    try:
        mk_semester_obj = MataKuliahSemester.objects.get(
            mk_kurikulum=new_mk_semester.mk_kurikulum,
            semester=semester_prodi_obj
        )
    except (MataKuliahSemester.DoesNotExist, MataKuliahSemester.MultipleObjectsReturned):
        message = 'Mata Kuliah Semester tidak dapat ditemukan. MK Kurikulum ID: {}, Semester ID: {}'.format(new_mk_semester.mk_kurikulum.id_neosia, semester_prodi_id)
        if settings.DEBUG: print(message) 
        return (is_success, message)
    
    if not hasattr(mk_semester_obj, 'rencanapembelajaransemester'):
        message = 'Mata kuliah {}, {}, tidak mempunyai RPS.'.format(mk_semester_obj.mk_kurikulum.nama, mk_semester_obj.semester.semester.nama)
        return (is_success, message)
    
    rps_obj: RencanaPembelajaranSemester = mk_semester_obj.rencanapembelajaransemester
    
    new_rps_obj = clone_object(
        rps_obj, 
        attrs={
            'mk_semester': new_mk_semester
        }
    )

    if new_rps_obj is not None:
        is_success = True
        message = 'Berhasil menduplikasi rincian RPS.'
    else:
        message = 'Gagal menduplikasi rincian RPS.'

    return (is_success, message)


def get_semester_choices_pertemuan_rps_duplicate(mk_semester: MataKuliahSemester):
    # Get All MK Semester in same kurikulum
    list_mk_semester: QuerySet[MataKuliahSemester] = mk_semester.mk_kurikulum.get_mk_semester()
    semester_choices = []

    for mk_semester_obj in list_mk_semester:
        # Skip the same semester
        if mk_semester_obj.pk is mk_semester.pk: continue
        
        # Skip if MK doesn't have pertemuan RPS
        list_pertemuan_rps_mk_semester: QuerySet[PertemuanRPS] = mk_semester_obj.get_all_pertemuan_rps()
        if not list_pertemuan_rps_mk_semester.exists(): continue

        semester_choice = mk_semester_obj.semester.id_neosia, '{}. <a href="{}?active_tab=pertemuan" target="_blank">Lihat RPS di sini</a>'.format(mk_semester_obj.semester.semester.nama, mk_semester_obj.get_rps_home_url())

        semester_choices.append(semester_choice)
    
    return semester_choices


def duplicate_pertemuan_rps(semester_prodi_id, new_mk_semester: MataKuliahSemester):
    is_success = False
    message = ''

    try:
        semester_prodi_obj = SemesterProdi.objects.get(id_neosia=semester_prodi_id)
    except (SemesterProdi.DoesNotExist, SemesterProdi.MultipleObjectsReturned):
        message = 'Semester Prodi tidak dapat ditemukan. ID: {}'.format(semester_prodi_id)
        if settings.DEBUG: print(message) 
        return (is_success, message) 
    
    try:    
        mk_semester_obj = MataKuliahSemester.objects.get(
            mk_kurikulum=new_mk_semester.mk_kurikulum,
            semester=semester_prodi_obj
        )
    except (MataKuliahSemester.DoesNotExist, MataKuliahSemester.MultipleObjectsReturned):
        message = 'Mata Kuliah Semester tidak dapat ditemukan. MK Kurikulum ID: {}, Semester ID: {}'.format(new_mk_semester.mk_kurikulum.id_neosia, semester_prodi_id)
        if settings.DEBUG: print(message) 
        return (is_success, message)

    # Get list pertemuan
    list_pertemuan_rps: QuerySet[PertemuanRPS] = mk_semester_obj.get_all_pertemuan_rps()
    cloned_list_pertemuan_rps = []

    for pertemuan in list_pertemuan_rps:
        new_pertemuan = clone_object(
            pertemuan,
            attrs={
                'mk_semester': new_mk_semester
            }
        )
        cloned_list_pertemuan_rps.append(new_pertemuan)
    
    if list_pertemuan_rps.count() == len(cloned_list_pertemuan_rps):
        is_success = True
        message = 'Berhasil menduplikasi rincian RPS.'
    else:
        message = 'Jumlah pertemuan yang diduplikasi hanya {} pertemuan. Ekspektasi: {}.'.format(len(cloned_list_pertemuan_rps), list_pertemuan_rps.count())

    return (is_success, message)
