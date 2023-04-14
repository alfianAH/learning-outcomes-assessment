import numpy as np
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from kurikulum.models import Kurikulum
from ilo.models import Ilo
from pi_area.models import PerformanceIndicator
from clo.models import (
    Clo, NilaiCloMataKuliahSemester,
    NilaiCloPeserta,
)
from mata_kuliah_semester.models import (
    MataKuliahSemester,
    PesertaMataKuliah,
)


User = get_user_model()


def calculate_ilo(list_bobot_mk: list, list_persentase_clo: list,
                  list_bobot_pi_ilo: list, list_nilai_clo: list,
                  nilai_max: int):
    """Calculate ILO

    Args:
        list_bobot_mk (list): list of bobot MK
        list_persentase_clo (list): List of persentase CLO
        list_bobot_pi_ilo (list): List of bobot PI ILO
        list_nilai_clo (list): List of nilai CLO Peserta or MK
        nilai_max (int): Nilai max

    Returns:
        (bool, float): 
            is_success: Is calculation success?
            persentase_capaian_ilo: ILO achievement score
    """

    is_success = False

    list_bobot_mk = np.array(list_bobot_mk)
    list_persentase_clo = np.array(list_persentase_clo)
    list_bobot_pi_ilo = np.array(list_bobot_pi_ilo)
    list_nilai_clo = np.array(list_nilai_clo)

    # Use try to prevent miss shape
    try:
        konversi_clo_to_ilo = (list_bobot_mk * list_persentase_clo * list_bobot_pi_ilo) * nilai_max
    except ValueError:
        message = 'Shape array tidak sama. Bobot MK: {} Persentase CPMK: {}, Bobot PI ILO: {}.'.format(
            list_bobot_mk.shape, list_persentase_clo.shape, list_bobot_pi_ilo.shape)
        if settings.DEBUG: print(message)
        return (is_success, None)
    
    # If mahasiswa doesn't have the ILO, just skip it
    if konversi_clo_to_ilo.shape[0] != 0:
        persentase_konversi = konversi_clo_to_ilo / np.sum(konversi_clo_to_ilo)
    else:
        return (is_success, None)

    # Use try to prevent miss shape
    try:
        persentase_capaian_ilo = persentase_konversi * list_nilai_clo
    except ValueError:
        message = 'Shape array tidak sama. Persentase Konversi: {}, Nilai CPMK: {}.'.format(
            persentase_konversi.shape, list_nilai_clo.shape)
        if settings.DEBUG: print(message)
        return (is_success, None)

    persentase_capaian_ilo = np.sum(persentase_capaian_ilo)
    is_success = True

    return (is_success, persentase_capaian_ilo)


def calculate_ilo_prodi(list_ilo: QuerySet[Ilo], 
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
            Example:
                result = {
                    'nama_ilo': nilai,
                    'nama_ilo': nilai,
                }
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
            # Check status nilai MK Semester
            if not mk_semester.status_nilai:
                message = 'Harap melengkapi nilai dari mata kuliah ({}, {}) terlebih dahulu'.format(
                    mk_semester.mk_kurikulum.nama, mk_semester.semester.semester)
                return (is_success, message, result)

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
                message = 'Mata Kuliah: {}, belum mempunyai Nilai CPMK.'.format(mk_semester.mk_kurikulum.nama)
                return (is_success, message, result)
        
        # Calculate ILO
        is_success, persentase_capaian_ilo = calculate_ilo(list_bobot_mk, list_persentase_clo, list_bobot_pi_ilo, list_nilai_clo_mk_semester, nilai_max)
        
        # Add to result
        if is_success:
            result[ilo.nama] = persentase_capaian_ilo
        else:
            result[ilo.nama] = None
            continue
    
    expected_len_mk_semester = list_mk_semester.count()
    # If calculated mk semester is not the same as in query, return
    if len(calculated_mk_semester) != expected_len_mk_semester:
        remaining_len_mk_semester = expected_len_mk_semester - len(calculated_mk_semester)

        message = 'Terdapat {} mata kuliah yang belum dihitung. Total yang sudah dihitung: {}, ekspektasi: {}'.format(remaining_len_mk_semester, len(calculated_mk_semester), expected_len_mk_semester)

        return (is_success, message, result)

    if len(result.keys()) != list_ilo.count():
        message = 'Panjang array List ILO dan hasil tidak sesuai. List ILO: {}, Hasil: {}.'.format(list_ilo.count(), len(result.keys()))
    else:
        is_success = True
        message = 'Berhasil menghitung capaian ILO Program Studi.'

    return (is_success, message, result)


def calculate_ilo_mahasiswa(list_ilo: QuerySet[Ilo], 
                            list_mahasiswa_as_peserta_mk: QuerySet[PesertaMataKuliah],
                            mahasiswa: User, 
                            max_sks_prodi: int, nilai_max: int):
    """Calculate nilai per ILO from list_mahasiswa_as_peserta_mk

    Args:
        list_ilo (QuerySet[Ilo]): Kurikulum's ILO QuerySet
        list_mahasiswa_as_peserta_mk (QuerySet[PesertaMataKuliah]): Peserta MK Queryset
        mahasiswa (User): Current mahasiswa (User)
        max_sks_prodi (int): SKS Max Kelulusan Prodi
        nilai_max (int): Nilai max

    Returns:
        (bool, str, list, list): 
            is_success: Is calculation success?
            message: Success or error message
            result: Result of calculation 
            Example:
                result = [{
                    'nama': 'nama_ilo',
                    'nilai': nilai_ilo,
                    'satisfactory_level: satisfactory_level_ilo
                }]
    """

    is_success = False
    message = ''
    result = []
    calculated_peserta = []
    
    # Loop through ILO
    for ilo in list_ilo:
        list_peserta_mk_ilo = list_mahasiswa_as_peserta_mk.filter(
            kelas_mk_semester__mk_semester__clo__piclo__performance_indicator__pi_area__ilo=ilo
        ).distinct()

        list_bobot_mk = []
        list_persentase_clo = []
        list_bobot_pi_ilo = []
        list_nilai_clo_peserta = []

        # Loop through MK Semester (peserta)
        for peserta_mk in list_peserta_mk_ilo:
            mk_semester = peserta_mk.kelas_mk_semester.mk_semester

            # Check status nilai
            if not peserta_mk.status_nilai:
                message = 'Harap melengkapi nilai dari {} di mata kuliah ({}, {}) terlebih dahulu'.format(
                    mahasiswa.nama, 
                    mk_semester.mk_kurikulum.nama,
                    mk_semester.semester)
                if settings.DEBUG: print(message)
                return (is_success, message, result)

            if peserta_mk not in calculated_peserta:
                calculated_peserta.append(peserta_mk)

            list_clo_ilo = Clo.objects.filter(
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

            # Get nilai CLO peserta
            nilai_clo_peserta_qs = NilaiCloPeserta.objects.filter(
                peserta=peserta_mk,
                clo__in=list_clo_ilo
            ).values_list('nilai')

            if nilai_clo_peserta_qs.exists():
                list_nilai_clo_peserta += [nilai_clo[0] for nilai_clo in nilai_clo_peserta_qs]
            else:
                message = 'Peserta: {} di Mata Kuliah: {}, {}, belum mempunyai Nilai CPMK.'.format(mahasiswa.nama, mk_semester.mk_kurikulum.nama, mk_semester.semester.semester)
                if settings.DEBUG: print(message)
                return (is_success, message, result)

        # Calculate ILO
        is_success, persentase_capaian_ilo = calculate_ilo(list_bobot_mk, list_persentase_clo, list_bobot_pi_ilo, list_nilai_clo_peserta, nilai_max)

        # Add to result
        if is_success:
            result.append({
                'nama': ilo.nama,
                'nilai': persentase_capaian_ilo,
                'satisfactory_level': ilo.satisfactory_level,
            })
        else:
            result.append({
                'nama': ilo.nama,
                'nilai': None,
                'satisfactory_level': ilo.satisfactory_level,
            })
            continue
    
    expected_len_peserta_mk = list_mahasiswa_as_peserta_mk.count()
    # If calculated mk semester is not the same as in query, return
    if len(calculated_peserta) != expected_len_peserta_mk:
        remaining_len_peserta = expected_len_peserta_mk - len(calculated_peserta)

        message = 'Terdapat {} peserta yang belum dihitung. Total yang sudah dihitung: {}, ekspektasi: {}'.format(remaining_len_peserta, len(calculated_peserta), expected_len_peserta_mk)

        return (is_success, message, result)
    
    is_success = True
    message = 'Berhasil menghitung capaian ILO Mahasiswa.'
    return (is_success, message, result)


def process_ilo_mahasiswa(list_ilo: QuerySet[Ilo], max_sks_prodi: int,
                          list_peserta_mk: QuerySet[PesertaMataKuliah],
                          is_semester_included: bool,
                          filter: list):
    """Calculate ILO All Mahasiswa in Kurikulum according to tahun ajaran and semester filter

    Args:
        list_ilo (QuerySet[Ilo]): QuerySet of ILO from kurikulum
        max_sks_prodi (int): Max SKS Kelulusan Prodi
        is_semester_included (bool): Is semester included in filter?
        filter (list): List of filtered tahun ajaran or semester (obj, name)

    Returns:
        (bool, str, dict): 
            is_success: Is calculation success?
            message: Success or error message
            result: Result of calculation
                Example:
                result = {
                    'nim': {
                        'nama': 'nama_mahasiswa',
                        'nim': 'nim_mahasiswa',
                        'result': [
                            'filter': 'tahun_ajaran or semester',
                            'result': [
                                {
                                    'nama': 'nama_ilo',
                                    'nilai': 'nilai_ilo',
                                    'satisfactory_level': satisfactory_level_ilo
                                }
                            ]
                        ]
                    }
                }
    """
    
    is_success = False
    message = ''
    result: dict = {}
    nilai_max = 100

    list_mahasiswa = User.objects.filter(
        pesertamatakuliah__in=list_peserta_mk
    ).distinct().order_by('-username')

    for mahasiswa in list_mahasiswa:
        result_mahasiswa = {
            'nim': mahasiswa.username,
            'nama': mahasiswa.nama,
            'read_detail_url': mahasiswa.get_laporan_cpl_url(),
            'result': []
        }

        # Loop through semester
        if is_semester_included:
            for semester_prodi_obj, semester_prodi_name in filter:
                # Get mahasiswa's mata kuliah participation
                list_mahasiswa_as_peserta_mk = list_peserta_mk.filter(
                    mahasiswa=mahasiswa,
                    kelas_mk_semester__mk_semester__semester=semester_prodi_obj
                )

                if list_mahasiswa_as_peserta_mk.exists():
                    # Proceed
                    is_success, message, calculation_result = calculate_ilo_mahasiswa(list_ilo, list_mahasiswa_as_peserta_mk, mahasiswa, max_sks_prodi, nilai_max)
                else:
                    # Just add empty list
                    is_success = True
                    calculation_result = []
                
                result_mahasiswa['result'].append({
                    'filter': semester_prodi_name,
                    'result': calculation_result
                })
                
                # Return if not success
                if not is_success: 
                    if settings.DEBUG: print('ILO Mahasiswa gagal.', message)
                    return (is_success, message, result)
        else:
            for tahun_ajaran_prodi_obj, tahun_ajaran_name in filter:
                list_mahasiswa_as_peserta_mk = list_peserta_mk.filter(
                    mahasiswa=mahasiswa,
                    kelas_mk_semester__mk_semester__semester__tahun_ajaran_prodi=tahun_ajaran_prodi_obj
                )

                if list_mahasiswa_as_peserta_mk.exists():
                    # Proceed
                    is_success, message, calculation_result = calculate_ilo_mahasiswa(list_ilo, list_mahasiswa_as_peserta_mk, mahasiswa, max_sks_prodi, nilai_max)
                else:
                    # Just add empty list
                    is_success = True
                    calculation_result = []
                
                result_mahasiswa['result'].append({
                    'filter': tahun_ajaran_name,
                    'result': calculation_result
                })

                # Return if not success
                if not is_success: 
                    if settings.DEBUG: print('ILO Mahasiswa gagal.', message)
                    return (is_success, message, result)
        
        if mahasiswa.username not in result.keys():
            result[mahasiswa.username] = result_mahasiswa

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


def process_ilo_prodi(list_ilo: QuerySet[Ilo], max_sks_prodi: int, 
                      is_semester_included: bool, 
                      filter: list):
    """Calculate ILO Prodi in Kurikulum according to tahun ajaran and semester filter

    Args:
        list_ilo (QuerySet[Ilo]): QuerySet of ILO from kurikulum
        max_sks_prodi (int): Max SKS Kelulusan Prodi
        is_semester_included (bool): Is semester included in filter?
        filter (list): List of filtered tahun ajaran or semester (obj, name)
    
    Returns:
        (bool, str, dict): 
            is_success: Is calculation success?
            message: Success or error message
            result: Result of calculation
                Example:
                result = {
                    'nama_semester': {
                        'nama_ilo': nilai,
                        'nama_ilo': nilai,
                    }
                }
    """
    is_success = False
    message = ''
    result = {}

    # Prepare all needed components
    nilai_max = 100

    # Calculate ILO Prodi
    # Get all mata kuliah semester
    if is_semester_included:
        for semester_prodi_obj, semester_nama in filter:
            # Get all mata kuliah semester
            list_mk_semester = MataKuliahSemester.objects.filter(
                semester=semester_prodi_obj
            ).distinct()
            
            # Calculate ILO Prodi
            is_success, message, calculation_result = calculate_ilo_prodi(list_ilo, list_mk_semester, max_sks_prodi, nilai_max)
            result.update({
                semester_nama: calculation_result
            })

            if not is_success: 
                if settings.DEBUG: print('ILO Prodi gagal.', message)
                return (is_success, message, result)
    else:
        for tahun_ajaran_prodi_obj, tahun_ajaran_nama in filter:
            list_mk_semester = MataKuliahSemester.objects.filter(
                semester__tahun_ajaran_prodi=tahun_ajaran_prodi_obj
            ).distinct()

            # Calculate ILO Prodi
            is_success, message, calculation_result = calculate_ilo_prodi(list_ilo, list_mk_semester, max_sks_prodi, nilai_max)
            
            result.update({
                tahun_ajaran_nama: calculation_result
            })

            if not is_success: 
                if settings.DEBUG: print('ILO Prodi gagal.', message)
                return (is_success, message, result)
    
    
    if len(result.keys()) != len(filter):
        is_success = False
        if is_semester_included:
            message = 'Panjang semester prodi tidak sesuai. Ekspektasi: {}, hasil: {}'.format(len(filter), len(result.keys()))
        else:
            message = 'Panjang tahun ajaran prodi tidak sesuai. Ekspektasi: {}, hasil: {}'.format(len(filter), len(result.keys()))
    else:
        is_success = True
  
    return (is_success, message, result)
