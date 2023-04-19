from functools import partial
from io import BytesIO
from copy import copy
import os
import uuid
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle,
    Frame, PageTemplate, Image
)
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from learning_outcomes_assessment.utils import export_pdf_header
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
        message = 'Shape array tidak sama. Bobot MK: {} Persentase CPMK: {}, Bobot PI CPL: {}.'.format(
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
        message = 'Panjang array List CPL dan hasil tidak sesuai. List CPL: {}, Hasil: {}.'.format(list_ilo.count(), len(result.keys()))
    else:
        is_success = True
        message = 'Berhasil menghitung capaian CPL Program Studi.'

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
    message = 'Berhasil menghitung capaian CPL Mahasiswa.'
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
                    if settings.DEBUG: print('Perhitungan CPL Mahasiswa gagal.', message)
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
                    if settings.DEBUG: print('Perhitungan CPL Mahasiswa gagal.', message)
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
                if settings.DEBUG: print('Perhitungan CPL Prodi gagal.', message)
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
                if settings.DEBUG: print('Perhitungan CPL Prodi gagal.', message)
                return (is_success, message, result)
    
    
    if len(result.keys()) != len(filter):
        is_success = False
        if is_semester_included:
            message = 'Banyak semester prodi tidak sesuai. Ekspektasi: {}, hasil: {}'.format(len(filter), len(result.keys()))
        else:
            message = 'Banyak tahun ajaran prodi tidak sesuai. Ekspektasi: {}, hasil: {}'.format(len(filter), len(result.keys()))
    else:
        is_success = True
  
    return (is_success, message, result)


def process_ilo_prodi_by_kurikulum(list_ilo: QuerySet[Ilo], max_sks_prodi: int, kurikulum: Kurikulum):
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

    # Prepare all needed components
    nilai_max = 100

     # Get all mata kuliah semester
    list_mk_semester = MataKuliahSemester.objects.filter(
        mk_kurikulum__kurikulum=kurikulum
    ).distinct()
    
    # Calculate ILO Prodi
    is_success, message, calculation_result = calculate_ilo_prodi(list_ilo, list_mk_semester, max_sks_prodi, nilai_max)
    result.update({
        kurikulum.nama: calculation_result
    })

    if not is_success: 
        if settings.DEBUG: print('Perhitungan CPL Prodi gagal.', message)
        return (is_success, message, result)
    
    # Check result key's length
    if len(result.keys()) == 1:
        is_success = True
    else:
        is_success = False
        message = 'Banyak kurikulum tidak sesuai. Ekspektasi: {}, hasil: {}'.format(1, len(result.keys()))

    return (is_success, message, result)


def process_ilo_mahasiswa_by_kurikulum(list_ilo: QuerySet[Ilo], max_sks_prodi: int, 
                                       list_peserta_mk: QuerySet[PesertaMataKuliah],
                                       kurikulum_obj: Kurikulum):
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
                        'result': [
                            'filter': 'kurikulum',
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
            return (is_success, message, result)
        
        if mahasiswa.username not in result.keys():
            result[mahasiswa.username] = result_mahasiswa

    return (is_success, message, result)


def generate_laporan_cpl_prodi_pdf(
        list_ilo: QuerySet[Ilo],
        list_filter,
        calculation_result: dict,
        prodi_name: str, fakultas_name: str,
):
    file_stream = BytesIO()

    # Create the PDF object, using the buffer as its "file."
    page_size = landscape(letter)
    pdf_file = SimpleDocTemplate(file_stream, pagesize=page_size)
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    empty_line = Spacer(1, 20)
    font_size = normal_style.fontSize

    # Title
    title = Paragraph(
        'Laporan Capaian Pembelajaran Lulusan Prodi',
        style=styles['h1']
    )

    header_style = copy(styles['h2'])
    header_style.alignment = TA_CENTER
    header_content = Paragraph(
        "UNIVERSITAS HASANUDDIN<br/>FAKULTAS {}<br/>PROGRAM STUDI {}".format(fakultas_name, prodi_name), 
        header_style
    )

    # Get the space before and after the paragraph
    space_before = header_content.getSpaceBefore()
    space_after = header_content.getSpaceAfter()

    # Get the height of the paragraph
    para_height = header_content.wrap(pdf_file.width, pdf_file.height)[1]

    # Calculate the total height of the block
    block_height = para_height + space_before + space_after

    frame = Frame(
        pdf_file.leftMargin, 
        pdf_file.bottomMargin, 
        pdf_file.width, 
        pdf_file.height - block_height
    )
    template = PageTemplate(
        frames=frame, 
        onPage=partial(
            export_pdf_header, 
            content=header_content,
            image_path='./static/public/img/logo-unhas.jpg',
            image_width=0.6*inch,
            image_height=0.75*inch,
        )
    )
    pdf_file.addPageTemplates([template])

    # Tabel detail spider chart
    table_spider_chart_title = Paragraph(
        'Tabel Pencapaian Capaian Pembelajaran Lulusan',
        style=styles['h2']
    )

    # (COL, ROW)
    table_style_data = [
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),               # Header align
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),    # Header font
        ('FONTSIZE', (0, 0), (-1, 0), 11),                  # Header font size
        ('TOPPADDING', (0, 0), (-1, 0), 12),                # Header top padding
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),             # Header bottom padding
        ('TOPPADDING', (0, 1), (-1, -1), 4),                # Body top padding
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),             # Body bottom padding
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),     # Grid
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),                # Body vertical align
    ]

    table_spider_chart_style = TableStyle(table_style_data)
    
    # Table spider chart
    len_table_spider_chart = len(list_filter) // 3
    if len(list_filter) % 3 > 0: len_table_spider_chart += 1
    
    list_table_spider_chart = []
    chart_data = {}
    
    for i in range(len_table_spider_chart):
        table_data = [['CPL', 'Satisfactory Level',]]
        
        # Calculate index subscriptable
        filter_index_start = i*3

        if len_table_spider_chart > 1:
            # If table is more than 1, ...
            if i+1 == len_table_spider_chart:
                filter_index_end = filter_index_start + len(list_filter) % 3
            else:
                filter_index_end = filter_index_start + 3
        else:
            # If table is only 1 row, ...
            filter_index_end = len(list_filter)
        
        # Make header for filter
        for filter in list_filter[filter_index_start:filter_index_end]:
            table_data[0].append(filter[1])

        # Table spider chart data
        for ilo in list_ilo:
            data = [ilo.nama, ilo.satisfactory_level]

            calcultation_result_sub = list(calculation_result.items())[filter_index_start:filter_index_end]
            for nama_filter, ilo_dict in calcultation_result_sub:
                # Set chart data
                if nama_filter not in chart_data.keys():
                    chart_data[nama_filter] = []
                
                for nama_ilo, nilai_ilo in ilo_dict.items():
                    # Skip if not current ILO
                    if nama_ilo != ilo.nama: continue

                    # Add nilai to row
                    if nilai_ilo is None: 
                        data.append('-')    
                        # Add chart data
                        chart_data[nama_filter].append(0)
                    else: 
                        nilai_ilo_formatted = float("{:.2f}".format(nilai_ilo))
                        data.append(nilai_ilo_formatted)
                        # Add chart data
                        chart_data[nama_filter].append(nilai_ilo_formatted)
                    
                    # Go to next filter
                    break

            # Append data
            table_data.append(data)
        
        spider_chart_table = Table(
            table_data,
            style=table_spider_chart_style,
            hAlign='LEFT',
        )

        list_table_spider_chart.append(spider_chart_table)
    
    # Chart ILO
    is_multiple_result = len(list_filter) > 1
    
    # If multiple result, bar and line chart
    # Else, radar chart
    if is_multiple_result:
        x_ticks = []
        satisfactory_level_data = []
        for ilo in list_ilo:
            x_ticks.append(ilo.nama)
            satisfactory_level_data.append(ilo.satisfactory_level)

        x = np.arange(len(x_ticks))  # the label locations
        width = 0.25  # the width of the bars
        multiplier = 0

        fig, ax = plt.subplots(layout='constrained')

        # Bar chart
        for nama_filter, list_nilai_ilo in chart_data.items():
            offset = width * multiplier
            ax.bar(
                x + offset, 
                list_nilai_ilo, 
                width, 
                label=nama_filter
            )
            multiplier += 1

        # Satisfactory level line chart
        ax.plot(
            x + (len(list_filter)-1) * width/2, 
            satisfactory_level_data, 
            marker='o', 
            color='dimgrey', 
            label='Satisfactory level'
        )

        # Styling
        ax.set_title('Laporan Capaian Pembelajaran Lulusan Program Studi')
        ax.set_xticks(x + (len(list_filter)-1) * width/2, x_ticks)
        ax.grid(True, axis='y', which='major')
        ax.grid(True, axis='x', which='minor')
        
        minor_locator = mticker.AutoMinorLocator(2) # set the number of minor intervals per major interval
        ax.xaxis.set_minor_locator(minor_locator)
        ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3), ncol=2)
        ax.set_ylim(0, 100)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#DDDDDD')
        
        # Save chart
        chart_filename = '{}.png'.format(uuid.uuid1())
        chart_dir =  os.path.join(settings.STATIC_ROOT, 'laporan_cpl', 'charts')
        if not os.path.exists(chart_dir):
            os.makedirs(chart_dir)
        
        chart_path = os.path.join(chart_dir, chart_filename)
        fig.set_size_inches(6, 4)
        fig.savefig(chart_path)
    else:
        pass

    chart_image = Image(chart_path)

    # Build
    pdf_file_elements = [
        title,
        table_spider_chart_title,
    ]
    for spider_chart_table in list_table_spider_chart:
        pdf_file_elements += [spider_chart_table, empty_line]
    
    pdf_file_elements += [
        chart_image,
    ]

    pdf_file.build(pdf_file_elements)
    
    # Close the PDF object cleanly
    file_stream.seek(0)

    return file_stream


def generate_laporan_cpl_mahasiswa_pdf(
        list_ilo: QuerySet[Ilo],
        list_filter,
        calculation_result: dict,
        prodi_name: str, fakultas_name: str,
):
    file_stream = BytesIO()

    # Create the PDF object, using the buffer as its "file."
    pdf_file = SimpleDocTemplate(file_stream)
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    font_size = normal_style.fontSize

    # Title
    title = Paragraph(
        'Laporan Capaian Pembelajaran Lulusan Mahasiswa',
        style=styles['h1']
    )

    header_style = styles['h2']
    header_style.alignment = TA_CENTER
    header_content = Paragraph(
        "UNIVERSITAS HASANUDDIN<br/>FAKULTAS {}<br/>PROGRAM STUDI {}".format(fakultas_name, prodi_name), 
        header_style
    )

    # Get the space before and after the paragraph
    space_before = header_content.getSpaceBefore()
    space_after = header_content.getSpaceAfter()

    # Get the height of the paragraph
    para_height = header_content.wrap(pdf_file.width, pdf_file.height)[1]

    # Calculate the total height of the block
    block_height = para_height + space_before + space_after

    frame = Frame(
        pdf_file.leftMargin, 
        pdf_file.bottomMargin, 
        pdf_file.width, 
        pdf_file.height - block_height
    )
    template = PageTemplate(
        frames=frame, 
        onPage=partial(
            export_pdf_header, 
            content=header_content,
            image_path='./static/public/img/logo-unhas.jpg',
            image_width=0.6*inch,
            image_height=0.75*inch,
        )
    )
    pdf_file.addPageTemplates([template])

    # Build
    pdf_file.build([
        title,
    ])
    
    # Close the PDF object cleanly
    file_stream.seek(0)

    return file_stream
