import json
from django.conf import settings
from ilo.models import Ilo
from kurikulum.models import Kurikulum
from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Count
from laporan_cpl.utils import (
    calculate_ilo_mahasiswa, 
    calculate_ilo_prodi,
    perolehan_nilai_ilo_graph,
    perolehan_nilai_ilo_prodi_graph,
    perolehan_nilai_ilo_mahasiswa_graph,
)
from mata_kuliah_semester.models import MataKuliahSemester, PesertaMataKuliah


User = get_user_model()


def process_ilo_prodi(
    list_ilo: QuerySet[Ilo], max_sks_prodi: int, 
    filter: list,
    is_multiple_result: bool, is_semester_included: bool
):
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
    perolehan_nilai_ilo_graph_json_response = perolehan_nilai_ilo_graph(list_ilo, is_multiple_result)

    # Prepare all needed components
    nilai_max = 100

    # Calculate ILO Prodi
    # Get all mata kuliah semester
    if is_semester_included:
        for semester_prodi_obj, semester_nama in filter:
            # Get all mata kuliah semester
            list_mk_semester = MataKuliahSemester.objects.annotate(
                num_peserta=Count('kelasmatakuliahsemester__pesertamatakuliah')
            ).filter(
                num_peserta__gt=0,
                semester=semester_prodi_obj,
                kelasmatakuliahsemester__pesertamatakuliah__nilai_akhir__isnull=False
            ).distinct()
            
            # Calculate ILO Prodi
            is_success, message, calculation_result = calculate_ilo_prodi(list_ilo, list_mk_semester, max_sks_prodi, nilai_max)
            result.update({
                semester_nama: calculation_result
            })

            if not is_success: 
                if settings.DEBUG: print('Perhitungan CPL Prodi gagal.', message)
                return (is_success, message, result, json.dumps(perolehan_nilai_ilo_graph_json_response))
    else:
        for tahun_ajaran_prodi_obj, tahun_ajaran_nama in filter:
            list_mk_semester = MataKuliahSemester.objects.annotate(
                num_peserta=Count('kelasmatakuliahsemester__pesertamatakuliah')
            ).filter(
                num_peserta__gt=0,
                semester__tahun_ajaran_prodi=tahun_ajaran_prodi_obj,
                kelasmatakuliahsemester__pesertamatakuliah__nilai_akhir__isnull=False
            ).distinct()

            # Calculate ILO Prodi
            is_success, message, calculation_result = calculate_ilo_prodi(list_ilo, list_mk_semester, max_sks_prodi, nilai_max)
            
            result.update({
                tahun_ajaran_nama: calculation_result
            })

            if not is_success: 
                if settings.DEBUG: print('Perhitungan CPL Prodi gagal.', message)
                return (is_success, message, result, json.dumps(perolehan_nilai_ilo_graph_json_response))
    
    
    if len(result.keys()) != len(filter):
        is_success = False
        if is_semester_included:
            message = 'Banyak semester prodi tidak sesuai. Ekspektasi: {}, hasil: {}'.format(len(filter), len(result.keys()))
        else:
            message = 'Banyak tahun ajaran prodi tidak sesuai. Ekspektasi: {}, hasil: {}'.format(len(filter), len(result.keys()))
    else:
        is_success = True
        perolehan_nilai_ilo_prodi_graph(result, perolehan_nilai_ilo_graph_json_response)
  
    return (is_success, message, result, json.dumps(perolehan_nilai_ilo_graph_json_response))


def process_ilo_mahasiswa(
    list_ilo: QuerySet[Ilo], max_sks_prodi: int,
    filter: list,
    is_multiple_result: bool,
    list_peserta_mk: QuerySet[PesertaMataKuliah], 
    is_semester_included: bool
):
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
                            'result': [{
                                {
                                    'nama': 'nama_ilo',
                                    'nilai': 'nilai_ilo',
                                    'satisfactory_level': satisfactory_level_ilo
                                }
                            }]
                        ]
                    }
                }
    """
    
    is_success = False
    message = ''
    result: dict = {}
    nilai_max = 100
    perolehan_nilai_ilo_graph_json_response = perolehan_nilai_ilo_graph(list_ilo, is_multiple_result)

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
                    if settings.DEBUG: print('Perhitungan CPL Mahasiswa gagal.', message)
                    return (is_success, message, result, json.dumps(perolehan_nilai_ilo_graph_json_response))
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
                    if settings.DEBUG: print('Perhitungan CPL Mahasiswa gagal.', message)
                    return (is_success, message, result, json.dumps(perolehan_nilai_ilo_graph_json_response))
        
        if mahasiswa.username not in result.keys():
            result[mahasiswa.username] = result_mahasiswa

    perolehan_nilai_ilo_mahasiswa_graph(result, perolehan_nilai_ilo_graph_json_response)
    return (is_success, message, result, json.dumps(perolehan_nilai_ilo_graph_json_response))


def process_ilo_prodi_by_kurikulum(
    list_ilo: QuerySet[Ilo], max_sks_prodi: int, 
    filter: list,
    is_multiple_result: bool
):
    """Calculate ILO Prodi in Kurikulum

    Args:
        list_ilo (QuerySet[Ilo]): QuerySet of ILO from kurikulum
        max_sks_prodi (int): Max SKS Kelulusan Prodi
        kurikulum (Kurikulum): Filtered kurikulum object
    
    Returns:
        (bool, str, dict): 
            is_success: Is calculation success?
            message: Success or error message
            result: Result of calculation
                Example:
                result = {
                    'nama_kurikulum': {
                        'nama_ilo': nilai,
                        'nama_ilo': nilai,
                    }
                }
    """
    is_success = False
    message = ''
    result = {}
    perolehan_nilai_ilo_graph_json_response = perolehan_nilai_ilo_graph(list_ilo, is_multiple_result)

    kurikulum_obj: Kurikulum = filter[0][0]

    # Prepare all needed components
    nilai_max = 100

     # Get all mata kuliah semester
    list_mk_semester = MataKuliahSemester.objects.annotate(
        num_peserta=Count('kelasmatakuliahsemester__pesertamatakuliah')
    ).filter(
        num_peserta__gt=0,
        mk_kurikulum__kurikulum=kurikulum_obj,
        kelasmatakuliahsemester__pesertamatakuliah__nilai_akhir__isnull=False
    ).distinct()
    
    # Calculate ILO Prodi
    is_success, message, calculation_result = calculate_ilo_prodi(list_ilo, list_mk_semester, max_sks_prodi, nilai_max)
    result.update({
        kurikulum_obj.nama: calculation_result
    })

    if not is_success: 
        if settings.DEBUG: print('Perhitungan CPL Prodi gagal.', message)
        return (is_success, message, result, json.dumps(perolehan_nilai_ilo_graph_json_response))
    
    # Check result key's length
    if len(result.keys()) == 1:
        is_success = True
        perolehan_nilai_ilo_prodi_graph(result, perolehan_nilai_ilo_graph_json_response)
    else:
        is_success = False
        message = 'Banyak kurikulum tidak sesuai. Ekspektasi: {}, hasil: {}'.format(1, len(result.keys()))

    return (is_success, message, result, json.dumps(perolehan_nilai_ilo_graph_json_response))


def process_ilo_mahasiswa_by_kurikulum(
    list_ilo: QuerySet[Ilo], max_sks_prodi: int, 
    filter: list,
    is_multiple_result: bool,
    list_peserta_mk: QuerySet[PesertaMataKuliah],
):
    """Calculate ILO All Mahasiswa in Kurikulum

    Args:
        list_ilo (QuerySet[Ilo]): QuerySet of ILO from kurikulum
        max_sks_prodi (int): Max SKS Kelulusan Prodi
        kurikulum (Kurikulum): Filtered kurikulum object

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
                        'result': [{
                            'filter': 'kurikulum',
                            'result': [
                                {
                                    'nama': 'nama_ilo',
                                    'nilai': 'nilai_ilo',
                                    'satisfactory_level': satisfactory_level_ilo
                                }
                            }]
                        ]
                    }
                }
    """

    is_success = False
    message = ''
    result: dict = {}
    nilai_max = 100
    perolehan_nilai_ilo_graph_json_response = perolehan_nilai_ilo_graph(list_ilo, is_multiple_result)
    kurikulum_obj = filter[0][0]

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

        # Get mahasiswa's mata kuliah participation
        list_mahasiswa_as_peserta_mk = list_peserta_mk.filter(
            mahasiswa=mahasiswa,
            kelas_mk_semester__mk_semester__mk_kurikulum__kurikulum=kurikulum_obj
        )

        if list_mahasiswa_as_peserta_mk.exists():
            # Proceed
            is_success, message, calculation_result = calculate_ilo_mahasiswa(list_ilo, list_mahasiswa_as_peserta_mk, mahasiswa, max_sks_prodi, nilai_max)
        else:
            # Just add empty list
            is_success = True
            calculation_result = []
        
        result_mahasiswa['result'].append({
            'filter': kurikulum_obj.nama,
            'result': calculation_result
        })
        
        # Return if not success
        if not is_success: 
            if settings.DEBUG: print('Perhitungan CPL Mahasiswa gagal.', message)
            return (is_success, message, result, json.dumps(perolehan_nilai_ilo_graph_json_response))
        
        if mahasiswa.username not in result.keys():
            result[mahasiswa.username] = result_mahasiswa

    perolehan_nilai_ilo_mahasiswa_graph(result, perolehan_nilai_ilo_graph_json_response)
    
    return (is_success, message, result, json.dumps(perolehan_nilai_ilo_graph_json_response))
