from django.conf import settings
from django.db.models import QuerySet
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
    JenisPertemuan,
    TipeDurasi,
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
    
    # Get koordinator RPS
    list_koordinator_rps: QuerySet[KoordinatorRPS] = rps_obj.get_koordinator_rps()

    # Get dosen pengampu RPS
    list_dosen_pengampu_rps: QuerySet[DosenPengampuRPS] = rps_obj.get_dosen_pengampu_rps()

    # Get MK Syarat RPS
    list_mk_syarat_rps: QuerySet[MataKuliahSyaratRPS] = rps_obj.get_mata_kuliah_syarat_rps()

    # Duplicate RPS
    new_rps = rps_obj
    new_rps._state.adding = True
    new_rps.pk = None
    new_rps.mk_semester = new_mk_semester
    new_rps.save()

    for pengembang_rps in list_pengembang_rps:
        new_pengembang_rps = pengembang_rps
        new_pengembang_rps._state.adding = True
        new_pengembang_rps.pk = None
        new_pengembang_rps.rps = new_rps
        new_pengembang_rps.save()

    for koordinator_rps in list_koordinator_rps:
        new_koordinator_rps = koordinator_rps
        new_koordinator_rps._state.adding = True
        new_koordinator_rps.pk = None
        new_koordinator_rps.rps = new_rps
        new_koordinator_rps.save()

    for dosen_pengampu_rps in list_dosen_pengampu_rps:
        new_dosen_pengampu_rps = dosen_pengampu_rps
        new_dosen_pengampu_rps._state.adding = True
        new_dosen_pengampu_rps.pk = None
        new_dosen_pengampu_rps.rps = new_rps
        new_dosen_pengampu_rps.save()

    for mk_syarat_rps in list_mk_syarat_rps:
        new_mk_syarat_rps = mk_syarat_rps
        new_mk_syarat_rps._state.adding = True
        new_mk_syarat_rps.pk = None
        new_mk_syarat_rps.rps = new_rps
        new_mk_syarat_rps.save()
    
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

    for pertemuan in list_pertemuan_rps:
        list_pembelajaran_pertemuan_rps: QuerySet[PembelajaranPertemuanRPS] = pertemuan.get_all_pembelajaran_pertemuan()

        list_durasi_pertemuan_rps: QuerySet[DurasiPertemuanRPS] = pertemuan.get_all_durasi_pertemuan()

        # Duplicate pertemuan
        new_pertemuan = pertemuan
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
        
        for pembelajaran_pertemuan_rps in list_pembelajaran_pertemuan_rps:
            new_pembelajaran_pertemuan_rps = pembelajaran_pertemuan_rps
            new_pembelajaran_pertemuan_rps._state.adding = True
            new_pembelajaran_pertemuan_rps.pk = None
            new_pembelajaran_pertemuan_rps.pertemuan_rps = new_pertemuan
            new_pembelajaran_pertemuan_rps.save()

        for durasi_pertemuan_rps in list_durasi_pertemuan_rps:
            new_durasi_pertemuan_rps = durasi_pertemuan_rps
            new_durasi_pertemuan_rps._state.adding = True
            new_durasi_pertemuan_rps.pk = None
            new_durasi_pertemuan_rps.pertemuan_rps = new_pertemuan
            new_durasi_pertemuan_rps.save()

    is_success = True
    message = 'Berhasil menduplikasi rincian RPS.'

    return (is_success, message)
