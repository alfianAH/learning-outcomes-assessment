import random
import time
from django.db.models import QuerySet
from django.conf import settings
from learning_outcomes_assessment.exceptions import ConditionTimeoutException
from learning_outcomes_assessment.utils import clone_object
from kurikulum.models import Kurikulum
from semester.models import SemesterProdi
from pi_area.models import (
    PerformanceIndicatorArea,
    PerformanceIndicator
)
from mata_kuliah_semester.models import MataKuliahSemester
from .models import Clo


def get_pi_area_by_kurikulum_choices(kurikulum_obj: Kurikulum):
    pi_area_qs = PerformanceIndicatorArea.objects.filter(assessment_area__kurikulum=kurikulum_obj)
    pi_area_choices = []

    for pi_area in pi_area_qs:
        # If PI Area doesn't have ILO, just print the code
        if not hasattr(pi_area, 'ilo'):
            pi_area_choice = pi_area.pk, pi_area.pi_code
        else:
            pi_area_choice = pi_area.pk, '{} - {}'.format(pi_area.pi_code, pi_area.ilo.nama)

        pi_area_choices.append(pi_area_choice)

    return pi_area_choices


def get_pi_by_pi_area_choices(pi_area_id):
    pi_qs = PerformanceIndicator.objects.filter(pi_area__id=pi_area_id)
    pi_choices = []

    for pi in pi_qs:
        pi_choice = pi.pk, pi.deskripsi

        pi_choices.append(pi_choice)
    
    return pi_choices


def get_semester_choices_clo_duplicate(mk_semester: MataKuliahSemester):
    # Get All MK Semester in same kurikulum
    list_mk_semester: QuerySet[MataKuliahSemester] = mk_semester.mk_kurikulum.get_mk_semester()
    semester_choices = []

    for mk_semester_obj in list_mk_semester:
        # Skip the same semester
        if mk_semester_obj.pk is mk_semester.pk: continue
        
        list_clo_mk_semester: QuerySet[Clo] = mk_semester_obj.get_all_clo()
        # If mk semester doesn't have CLO, skip
        if not list_clo_mk_semester.exists(): continue
        
        semester_choice = mk_semester_obj.semester.id_neosia, '{}. <a href="{}" target="_blank">Lihat CLO di sini</a>'.format(mk_semester_obj.semester.semester.nama, mk_semester_obj.get_clo_read_all_url())

        semester_choices.append(semester_choice)
    
    return semester_choices


def duplicate_clo(semester_prodi_id: int, new_mk_semester: MataKuliahSemester):
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
    
    list_clo: QuerySet[Clo] = mk_semester_obj.get_all_clo()
    cloned_list_clo = []

    for clo in list_clo:
        new_clo = clone_object(
            clo,
            attrs={
                'mk_semester': new_mk_semester
            }
        )
        cloned_list_clo.append(new_clo)
    
    if list_clo.count() == len(cloned_list_clo):
        is_success = True
        message = 'Berhasil menduplikasi CLO ke mata kuliah ini.'
    else:
        message = 'Jumlah pertemuan yang diduplikasi hanya {} pertemuan. Ekspektasi: {}.'.format(len(cloned_list_clo), list_clo.count())

    return (is_success, message)


def generate_nilai_clo(persentase_komponen_clo, nilai_akhir: float, timeout = 10):
    possibility_choices = {
        'low': {
            'choices': list(range(16)),
            'weights': [5 if i == 0 else 1 for i in range(16)]
        }
    }
    batas = {
        90: (20, 17), 
        80: (19, 12), 
        70: (18, 10),
        60: (16, 6), 
        50: (16, 0)
    }
    start_time = time.time()

    komponen_clo_len = len(persentase_komponen_clo)
    hasil = [0] * komponen_clo_len

    # Jika nilai 100
    if nilai_akhir == 100:
        for x in range(komponen_clo_len):
            hasil[x] = 100

    # Jika nilai 50-99
    if (nilai_akhir < 100) and (nilai_akhir >= 50):
        k = nilai_akhir - (nilai_akhir % 10)
        b_atas = batas[k][0]
        b_bawah = batas[k][1]

        while True:
            temp = 0
            for x in range(komponen_clo_len - 1):
                hasil[x] = random.randint(b_bawah, b_atas) * 5
                temp += hasil[x] * persentase_komponen_clo[x] / 100
            
            # Rumus: nilai (0-100) * persen = nilai diskon
            # Nilai sisa = nilai akhir - jumlah nilai sampai index sebelum terakhir
            # Nilai di komponen terakhir (0-100) = nilai sisa (nilai diskon) * 100 / persen
            hasil[komponen_clo_len - 1] = int((nilai_akhir - temp) * 100 / persentase_komponen_clo[komponen_clo_len - 1])
            if hasil[komponen_clo_len - 1] <= nilai_akhir and hasil[komponen_clo_len - 1] >= 0: break

            # Check if the timeout has been exceeded
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                raise ConditionTimeoutException("Kondisi generate nilai tidak terpenuhi dalam periode timeout {}".format(timeout))

    # Jika nilai 1-49
    if 50 > nilai_akhir > 0:
        # Pilih index untuk memberi nilai 0
        nol = random.randint(0, komponen_clo_len - 1)
        possibility_choice = possibility_choices['low']

        while True:
            temp = 0
            for x in range(komponen_clo_len - 1):
                if x != nol: 
                    random_number = random.choices(possibility_choice['choices'], possibility_choice['weights'])[0]
                    hasil[x] = random_number * 5
                temp += hasil[x] * persentase_komponen_clo[x] / 100
            
            # Nilai akhir - jumlah nilai sampai index sebelum terakhir 
            # tidak boleh lebih kecil dari 0
            # Supaya setidaknya nilai di index terakhir bisa ada 0 atau lebih
            if nilai_akhir - temp < 0: continue

            # Rumus: nilai (0-100) * persen = nilai diskon
            # Nilai sisa = nilai akhir - jumlah nilai sampai index sebelum terakhir
            # Nilai di komponen terakhir (0-100) = nilai sisa (nilai diskon) * 100 / persen
            hasil[komponen_clo_len - 1] = round((nilai_akhir - temp) * 100 / persentase_komponen_clo[komponen_clo_len - 1])
            if hasil[komponen_clo_len - 1] <= 95 and hasil[komponen_clo_len - 1] >= 0: break

            # Check if the timeout has been exceeded
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                raise ConditionTimeoutException("Kondisi generate nilai tidak terpenuhi dalam periode timeout {}".format(timeout))

    return hasil
