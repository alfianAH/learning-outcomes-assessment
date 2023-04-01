from copy import copy
from django.conf import settings
from django.db.models import QuerySet
from mata_kuliah_semester.models import MataKuliahSemester
from .models import (
    DosenPengampuRPS,
    DurasiPertemuanRPS,
    KoordinatorRPS,
    MataKuliahSyaratRPS,
    PembelajaranPertemuanRPS,
    PengembangRPS,
    RencanaPembelajaranSemester,
    PertemuanRPS,
    RincianPertemuanRPS,
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
    
    # Get pengembang RPS
    list_pengembang_rps: QuerySet[PengembangRPS] = rps_obj.get_pengembang_rps()
    # print(list_pengembang_rps.count())
    
    # Get koordinator RPS
    list_koordinator_rps: QuerySet[KoordinatorRPS] = rps_obj.get_koordinator_rps()

    # Get dosen pengampu RPS
    list_dosen_pengampu_rps: QuerySet[DosenPengampuRPS] = rps_obj.get_dosen_pengampu_rps()

    # Get MK Syarat RPS
    list_mk_syarat_rps: QuerySet[MataKuliahSyaratRPS] = rps_obj.get_mata_kuliah_syarat_rps()

    # Duplicate RPS
    new_rps = copy(rps_obj)
    new_rps._state.adding = True
    new_rps.pk = None
    new_rps.mk_semester = new_mk_semester
    new_rps.save()

    def duplicate_dosen(list_obj, new_rps):
        for obj in list_obj:
            new_obj = copy(obj)
            new_obj._state.adding = True
            new_obj.pk = None
            new_obj.rps = new_rps
            new_obj.save()

    duplicate_dosen(list_pengembang_rps, new_rps)
    duplicate_dosen(list_koordinator_rps, new_rps)
    duplicate_dosen(list_dosen_pengampu_rps, new_rps)
    duplicate_dosen(list_mk_syarat_rps, new_rps)
    
    is_success = True
    message = 'Berhasil menduplikasi rincian RPS.'

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

    def duplicate_pertemuan_rps(list_obj, new_pertemuan):
        for obj in list_obj:
            new_obj = copy(obj)
            new_obj._state.adding = True
            new_obj.pk = None
            new_obj.pertemuan_rps = new_pertemuan
            new_obj.save()

    for pertemuan in list_pertemuan_rps:
        list_pembelajaran_pertemuan_rps: QuerySet[PembelajaranPertemuanRPS] = pertemuan.get_all_pembelajaran_pertemuan()

        list_durasi_pertemuan_rps: QuerySet[DurasiPertemuanRPS] = pertemuan.get_all_durasi_pertemuan()

        # Duplicate pertemuan
        new_pertemuan = copy(pertemuan)
        new_pertemuan._state.adding = True
        new_pertemuan.pk = None
        new_pertemuan.mk_semester = new_mk_semester
        new_pertemuan.save()
        
        # Duplicate rincian pertemuan
        if hasattr(pertemuan, 'rincianpertemuanrps'):
            rincian_pertemuan_rps: RincianPertemuanRPS = pertemuan.rincianpertemuanrps

            new_rincian_pertemuan_rps = rincian_pertemuan_rps
            new_rincian_pertemuan_rps._state.adding = True
            new_rincian_pertemuan_rps.pk = None
            new_rincian_pertemuan_rps.pertemuan_rps = new_pertemuan
            new_rincian_pertemuan_rps.save()
        
        duplicate_pertemuan_rps(list_pembelajaran_pertemuan_rps, new_pertemuan)
        duplicate_pertemuan_rps(list_durasi_pertemuan_rps, new_pertemuan)

    return (is_success, message)
