import numpy as np
from django.conf import settings
from django.db.models import QuerySet
from kurikulum.models import Kurikulum
from semester.models import(
    TahunAjaranProdi, 
    SemesterProdi
)
from ilo.models import Ilo
from pi_area.models import PerformanceIndicator
from clo.models import Clo, NilaiCloMataKuliahSemester
from mata_kuliah_semester.models import MataKuliahSemester


def calculate_ilo(list_ilo: QuerySet[Ilo], 
                  list_mk_semester: QuerySet[MataKuliahSemester], 
                  max_sks_prodi: int, nilai_max: int):
    """Calculate nilai per ILO from list_ilo and list_mk_semester

    Args:
        list_ilo (QuerySet[Ilo]): Kurikulum's ILO QuerySet
        list_mk_semester (QuerySet[MataKuliahSemester]): Mata Kuliah Semester QuerySet
        max_sks_prodi (int): SKS Max Kelulusan Prodi
        nilai_max (int): Nilai max

    Returns:
        (bool, str, dict): 
            is_success: Is calculation success?
            message: Success or error message
            result: Result of calculation 
    """

    is_success = False
    message = ''
    result = {}
    calculated_mk_semester = []

    # Loop through ILO
    for ilo in list_ilo:
        # Get all mata kuliah semester
        list_mk_semester_ilo = list_mk_semester.filter(
            clo__piclo__performance_indicator__pi_area__ilo=ilo
        ).distinct()
        
        list_bobot_mk = []
        list_persentase_clo = []
        list_bobot_pi_ilo = []
        list_nilai_clo_mk_semester = []

        # Loop through MK Semester
        for mk_semester in list_mk_semester_ilo:
            # Add MK Semester to calculated_mk_semester
            if mk_semester not in calculated_mk_semester:
                calculated_mk_semester.append(mk_semester)

            list_clo_ilo: QuerySet[Clo] = Clo.objects.filter(
                mk_semester=mk_semester,
                piclo__performance_indicator__pi_area__ilo=ilo,
            ).distinct()

            # Get bobot MK
            list_bobot_mk += [mk_semester.mk_kurikulum.sks / max_sks_prodi for _ in range(list_clo_ilo.count())]

            # Get list persentase CLO
            list_persentase_clo += [
                clo.get_total_persentase_komponen()/100 for clo in list_clo_ilo
            ]

            # Get list bobot PI
            list_pi_ilo = PerformanceIndicator.objects.filter(
                pi_area__ilo=ilo
            )
            list_bobot_pi_ilo += [
                clo.get_pi_clo().count() / list_pi_ilo.count() for clo in list_clo_ilo
            ]

            # Get nilai CLO MK
            nilai_clo_mk_semester_qs = NilaiCloMataKuliahSemester.objects.filter(
                mk_semester=mk_semester,
                clo__in=list_clo_ilo
            ).values_list('nilai')

            if nilai_clo_mk_semester_qs.exists():
                list_nilai_clo_mk_semester += [nilai_clo[0] for nilai_clo in nilai_clo_mk_semester_qs]
            else:
                message = 'Mata Kuliah: {}, belum mempunyai Nilai CLO.'.format(mk_semester.mk_kurikulum.nama)
                return (is_success, message, result)
        
        list_bobot_mk = np.array(list_bobot_mk)
        list_persentase_clo = np.array(list_persentase_clo)
        list_bobot_pi_ilo = np.array(list_bobot_pi_ilo)
        list_nilai_clo_mk_semester = np.array(list_nilai_clo_mk_semester)

        # Use try to prevent miss shape
        try:
            konversi_clo_to_ilo = (list_bobot_mk * list_persentase_clo * list_bobot_pi_ilo) * nilai_max
        except ValueError:
            message = 'Shape array tidak sama. Bobot MK: {} Persentase CLO: {}, Bobot PI ILO: {}.'.format(
                list_bobot_mk.shape, list_persentase_clo.shape, list_bobot_pi_ilo.shape)
            if settings.DEBUG: print(message)
            continue

        persentase_konversi = konversi_clo_to_ilo / np.sum(konversi_clo_to_ilo)

        # Use try to prevent miss shape
        try:
            persentase_capaian_ilo = persentase_konversi * list_nilai_clo_mk_semester
        except ValueError:
            message = 'Shape array tidak sama. Persentase Konversi: {}, Nilai CLO MK: {}.'.format(
                persentase_konversi.shape, list_nilai_clo_mk_semester.shape)
            if settings.DEBUG: print(message)
            continue

        persentase_capaian_ilo = np.sum(persentase_capaian_ilo)
        
        result[ilo.nama] = persentase_capaian_ilo
    
    expected_len_mk_semester = list_mk_semester.count()
    # If calculated mk semester is not the same as in query, return
    if len(calculated_mk_semester) != expected_len_mk_semester:
        remaining_len_mk_semester = expected_len_mk_semester - len(calculated_mk_semester)

        message = 'Terdapat {} mata kuliah yang belum dihitung. Ekspektasi: {}'.format(remaining_len_mk_semester, expected_len_mk_semester)

        return (is_success, message, result)

    if len(result.keys()) != list_ilo.count():
        message = 'Panjang array List ILO dan hasil tidak sesuai. List ILO: {}, Hasil: {}.'.format(list_ilo.count(), len(result.keys()))
    else:
        is_success = True
        message = 'Berhasil menghitung capaian ILO.'

    return (is_success, message, result)


def get_ilo_and_sks_from_kurikulum(kurikulum_obj: Kurikulum):
    """Get ILO and max SKS prodi

    Args:
        kurikulum_id (str): Kurikulum ID

    Returns:
        (QuerySet[ILO], int): QuerySet of ILO and max SKS Prodi
    """

    list_ilo: QuerySet[Ilo] = Ilo.objects.filter(
        pi_area__assessment_area__kurikulum=kurikulum_obj
    )

    max_sks_prodi = kurikulum_obj.prodi_jenjang.total_sks_lulus

    return (list_ilo, max_sks_prodi)


def process_filter_laporan_cpl(list_ilo: QuerySet[Ilo], max_sks_prodi: int, 
                  is_semester_included: bool, 
                  filter_dict: dict):
    """Calculate ILO in Kurikulum according to tahun ajaran and semester filter

    Args:
        list_ilo (QuerySet[Ilo]): QuerySet of ILO from kurikulum
        max_sks_prodi (int): Max SKS Kelulusan Prodi
        is_semester_included (bool): Is semester included in filter?
        filter_dict (dict): Dictionary of filtered tahun ajaran and semester
    
    Returns:
        (bool, str, dict): 
            is_success: Is calculation success?
            message: Success or error message
            result: Result of calculation 
    """

    is_success = False
    message = ''
    result = {}

    # Prepare all needed components
    nilai_max = 100
    len_semester_prodi = 0

    for tahun_ajaran_prodi_id, list_semester_prodi_id in filter_dict.items():
        # Get all mata kuliah semester
        if is_semester_included:
            for semester_prodi_id in list_semester_prodi_id:
                len_semester_prodi += 1
                try:
                    semester_prodi_obj = SemesterProdi.objects.get(
                        id_neosia=semester_prodi_id
                    )
                except SemesterProdi.DoesNotExist:
                    message = 'Semester Prodi (ID={}) tidak ada di database.'.format(semester_prodi_id)
                    if settings.DEBUG: print(message)
                    return (is_success, message, result)
                except SemesterProdi.MultipleObjectsReturned:
                    message = 'Semester Prodi (ID={}) mengembalikan multiple object.'.format(semester_prodi_id)
                    if settings.DEBUG: print(message)
                    return (is_success, message, result)
                
                # Get all mata kuliah semester
                list_mk_semester = MataKuliahSemester.objects.filter(
                    semester=semester_prodi_obj
                ).distinct()
                
                # Calculate ILO
                is_success, message, calculation_result = calculate_ilo(list_ilo, list_mk_semester, max_sks_prodi, nilai_max)
                
                result[str(semester_prodi_obj.semester)] = calculation_result

                if not is_success:
                    return(is_success, message, result)
        else:
            try:
                tahun_ajaran_prodi_obj = TahunAjaranProdi.objects.get(
                    id=tahun_ajaran_prodi_id
                )
            except TahunAjaranProdi.DoesNotExist:
                message = 'TahunAjaranProdi (ID={}) tidak ada di database.'.format(tahun_ajaran_prodi_id)
                if settings.DEBUG: print(message)
                return (is_success, message, result)
            except TahunAjaranProdi.MultipleObjectsReturned:
                message = 'TahunAjaranProdi (ID={}) mengembalikan multiple object.'.format(tahun_ajaran_prodi_id)
                if settings.DEBUG: print(message)
                return (is_success, message, result)

            list_mk_semester = MataKuliahSemester.objects.filter(
                semester__tahun_ajaran_prodi=tahun_ajaran_prodi_obj
            ).distinct()

            # Calculate ILO
            is_success, message, calculation_result = calculate_ilo(list_ilo, list_mk_semester, max_sks_prodi, nilai_max)
            
            result[str(tahun_ajaran_prodi_obj.tahun_ajaran)] = calculation_result

            if not is_success:
                return(is_success, message, result)
    
    if is_semester_included:
        if len(result.keys()) != len_semester_prodi:
            is_success = False
            message = 'Panjang semester prodi tidak sesuai. Ekspektasi: {}, hasil: {}'.format(len_semester_prodi, len(result.keys()))
        else:
            is_success = True
    else:
        if len(result.keys()) != len(filter_dict.keys()):
            is_success = False
            message = 'Panjang tahun ajaran prodi tidak sesuai. Ekspektasi: {}, hasil: {}'.format(len(filter_dict.keys()), len(result.keys()))
        else:
            is_success = True

    return(is_success, message, result)
