import numpy as np
from django.conf import settings
from django.db.models import QuerySet
from learning_outcomes_assessment.utils import request_data_to_neosia
from .models import (
    KelasMataKuliahSemester,
    MataKuliahSemester,
    PesertaMataKuliah,
)
from clo.models import (
    Clo,
    KomponenClo,
    NilaiKomponenCloPeserta,
    NilaiCloMataKuliahSemester,
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


def get_peserta_kelas_mk_semester(mk_semester: MataKuliahSemester):
    list_peserta = []
    list_kelas_mk_semester: QuerySet[KelasMataKuliahSemester] = mk_semester.get_kelas_mk_semester()

    for kelas_mk_semester in list_kelas_mk_semester:
        parameters = {
            'id_kelas': kelas_mk_semester.id_neosia
        }

        json_response = request_data_to_neosia(PESERTA_MATA_KULIAH_URL, parameters)
        if json_response is None: return list_peserta

        for peserta_data in json_response:
            if peserta_data['id'] is None: continue

            try:
                nilai_akhir_response = float(peserta_data['nilai_akhir'])
            except ValueError: 
                if settings.DEBUG:
                    print('Cannot convert {} to float.'.format(peserta_data['nilai_akhir']))
                break
            except TypeError:
                # Nilai akhir from Neosia maybe null
                nilai_akhir_response = peserta_data['nilai_akhir']

            peserta = {
                'id_neosia': peserta_data['id'],
                'id_kelas_mk_semester': peserta_data['id_kelas_kuliah'],
                'mahasiswa': {
                    'username': peserta_data['nim'],
                    'nama': peserta_data['nama_mahasiswa'],
                },
                'nama': peserta_data['nama_mahasiswa'],
                'nilai_akhir': nilai_akhir_response,
                'nilai_huruf': peserta_data['nilai_huruf'],
            }

            list_peserta.append(peserta)

    return list_peserta


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


def get_peserta_kelas_mk_semester_choices(mk_semester: MataKuliahSemester):
    peserta_choices = []

    list_peserta_response = get_peserta_kelas_mk_semester(mk_semester)

    for peserta in list_peserta_response:
        id_peserta = peserta['id_neosia']
        
        peserta_qs = PesertaMataKuliah.objects.filter(id_neosia=id_peserta)
        
        # Skip peserta, if already in database
        if peserta_qs.exists(): continue

        peserta_choice = id_peserta, peserta
        peserta_choices.append(peserta_choice)
    
    return peserta_choices


def get_update_peserta_mk_semester_choices(mk_semester: MataKuliahSemester):
    list_peserta_mk_semester: QuerySet[PesertaMataKuliah] = mk_semester.get_all_peserta_mk_semester()
    list_peserta_mk_semester_response = get_peserta_kelas_mk_semester(mk_semester)
    update_peserta_mk_semester_choices = []

    for peserta in list_peserta_mk_semester:
        for peserta_response in list_peserta_mk_semester_response:
            if peserta.id_neosia != peserta_response['id_neosia']: continue
            
            # Check:
            # *Nilai akhir
            # *Nilai huruf
            isDataOkay = peserta.nilai_akhir == peserta_response['nilai_akhir'] and peserta.nilai_huruf == peserta_response['nilai_huruf']

            if isDataOkay: break

            update_peserta_mk_data = {
                'new': peserta_response,
                'old': peserta
            }

            update_peserta_mk_choice = peserta.id_neosia, update_peserta_mk_data

            update_peserta_mk_semester_choices.append(update_peserta_mk_choice)
            break
    
    return update_peserta_mk_semester_choices


def calculate_nilai_per_clo_mk_semester(mk_semester: MataKuliahSemester):
    list_peserta_mk: list[PesertaMataKuliah] = mk_semester.get_all_peserta_mk_semester()
    list_clo: QuerySet[Clo] = mk_semester.get_all_clo()
    
    average_clo_achievement = 0

    # Loop through CLO
    for clo_obj in list_clo:
        list_komponen_clo: QuerySet[KomponenClo] = clo_obj.get_komponen_clo()
        clo_achievement_components = []

        # Loop through komponen CLO
        for komponen_clo_obj in list_komponen_clo:
            list_nilai_komponen_all_peserta = []

            # Loop through peserta MK Semester
            for peserta in list_peserta_mk:
                # Get nilai komponen CLO peserta
                nilai_komponen_peserta: QuerySet[NilaiKomponenCloPeserta] = peserta.get_nilai_komponen_clo_peserta(komponen_clo_obj)
                
                list_nilai_komponen_all_peserta.append(nilai_komponen_peserta.first().nilai)

            # Calculate average of list nilai komponen of all peserta
            average_assessment_form = np.average(list_nilai_komponen_all_peserta)

            clo_achievement_components.append({
                'average_assessment_form': average_assessment_form,
                'persentase_komponen': komponen_clo_obj.persentase
            })
        
        # Loop through average assessment form to get clo achievement
        clo_achievement = 0
        clo_percentage = clo_obj.get_total_persentase_komponen()
        for clo_achievement_component in clo_achievement_components:
            # Calculate CLO achievement
            clo_achievement += (100 / clo_percentage) * (clo_achievement_component['persentase_komponen']/100) * clo_achievement_component['average_assessment_form']

        # Save clo_achievement to database
        nilai_clo_mk_semester, _ = NilaiCloMataKuliahSemester.objects.get_or_create(
            clo=clo_obj,
            mk_semester=mk_semester,
        )

        nilai_clo_mk_semester.nilai = clo_achievement
        nilai_clo_mk_semester.save()

        # Sum all CLO Achievement
        average_clo_achievement += clo_percentage * clo_achievement
    
    return clo_achievement
