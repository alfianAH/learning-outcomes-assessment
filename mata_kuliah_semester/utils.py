import numpy as np
import openpyxl
from io import BytesIO
from openpyxl.styles import (
    Font, Alignment, Border, Side, Protection
)
from openpyxl.worksheet.worksheet import Worksheet
from django.conf import settings
from django.db.models import QuerySet
from learning_outcomes_assessment.utils import request_data_to_neosia
from .models import (
    KelasMataKuliahSemester,
    MataKuliahSemester,
    PesertaMataKuliah,
    NilaiMataKuliahIloMahasiswa,
)
from clo.models import (
    Clo,
    KomponenClo,
    NilaiKomponenCloPeserta,
    NilaiCloMataKuliahSemester,
    NilaiCloPeserta,
)
from pi_area.models import PerformanceIndicator
from ilo.models import Ilo
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
    list_clo: QuerySet[Clo] = mk_semester.get_all_clo()
    
    average_clo_achievement = 0

    # Loop through CLO
    for clo_obj in list_clo:
        list_komponen_clo: QuerySet[KomponenClo] = clo_obj.get_komponen_clo()
        list_assessment_form = np.zeros((1, len(list_komponen_clo)))
        list_persentase_komponen = np.zeros((len(list_komponen_clo), 1))

        # Loop through komponen CLO
        for i, komponen_clo_obj in enumerate(list_komponen_clo):
            nilai_komponen_all_peserta = NilaiKomponenCloPeserta.objects.filter(
                komponen_clo=komponen_clo_obj
            )

            # Calculate average of list nilai komponen of all peserta
            average_assessment_form = np.average([nilai_komponen_peserta.nilai for nilai_komponen_peserta in nilai_komponen_all_peserta])
            
            # If average assessment form is NaN, set it to 0
            if np.isnan(average_assessment_form):
                average_assessment_form = 0

            list_assessment_form[0][i] = average_assessment_form
            list_persentase_komponen[i][0] = komponen_clo_obj.persentase
        
        # Loop through average assessment form to get clo achievement
        clo_achievement = 0
        clo_percentage = clo_obj.get_total_persentase_komponen()
        # Calculate CLO achievement
        clo_achievement = 1/clo_percentage * (list_assessment_form @ list_persentase_komponen).flatten()[0]

        # Save clo_achievement to database
        nilai_clo_mk_semester, _ = NilaiCloMataKuliahSemester.objects.get_or_create(
            clo=clo_obj,
            mk_semester=mk_semester,
        )

        nilai_clo_mk_semester.nilai = clo_achievement
        nilai_clo_mk_semester.save()

        # Sum all CLO Achievement
        average_clo_achievement += clo_percentage/100 * clo_achievement
    
    if mk_semester.average_clo_achievement is None:
        mk_semester.average_clo_achievement = average_clo_achievement
        mk_semester.save()
    else:
        if mk_semester.average_clo_achievement != average_clo_achievement:
            mk_semester.average_clo_achievement = average_clo_achievement
            mk_semester.save()


def calculate_nilai_per_clo_peserta(peserta: PesertaMataKuliah):
    list_clo: QuerySet[Clo] = peserta.kelas_mk_semester.mk_semester.get_all_clo()

    # Loop through CLO
    for clo_obj in list_clo:
        list_komponen_clo: QuerySet[KomponenClo] = clo_obj.get_komponen_clo()
        list_assessment_form = np.zeros((1, len(list_komponen_clo)))
        list_persentase_komponen = np.zeros((len(list_komponen_clo), 1))

        # Loop through komponen CLO
        for i, komponen_clo_obj in enumerate(list_komponen_clo):
            # Get nilai komponen CLO peserta
            nilai_komponen_peserta: QuerySet[NilaiKomponenCloPeserta] = peserta.get_nilai_komponen_clo_peserta(komponen_clo_obj)
            
            if nilai_komponen_peserta.first() is None: average_assessment_form = 0
            else:
                average_assessment_form = nilai_komponen_peserta.first().nilai

            list_assessment_form[0][i] = average_assessment_form
            list_persentase_komponen[i][0] = komponen_clo_obj.persentase
        
        # Loop through average assessment form to get clo achievement
        clo_achievement = 0
        clo_percentage = clo_obj.get_total_persentase_komponen()
        # Calculate CLO achievement
        clo_achievement = 1/clo_percentage * (list_assessment_form @ list_persentase_komponen).flatten()[0]

        # Save clo_achievement to database
        nilai_clo_peserta, _ = NilaiCloPeserta.objects.get_or_create(
            clo=clo_obj,
            peserta=peserta,
        )

        nilai_clo_peserta.nilai = clo_achievement
        nilai_clo_peserta.save()


def calculate_nilai_per_ilo_mahasiswa(peserta: PesertaMataKuliah):
    mk_semester = peserta.kelas_mk_semester.mk_semester
    list_ilo: QuerySet[Ilo] = Ilo.objects.filter(
        pi_area__performanceindicator__piclo__clo__mk_semester=mk_semester
    ).distinct()

    # Calculate all needed components
    max_sks_prodi = mk_semester.mk_kurikulum.kurikulum.prodi_jenjang.total_sks_lulus
    bobot_mk = mk_semester.mk_kurikulum.sks / max_sks_prodi
    nilai_max = 100

    # Loop through ILO
    for ilo in list_ilo:
        list_clo_ilo = Clo.objects.filter(
            mk_semester=mk_semester,
            piclo__performance_indicator__pi_area__ilo=ilo,
        ).distinct()

        # Get list persentase CLO
        list_persentase_clo = np.array([
            clo.get_total_persentase_komponen()/100 for clo in list_clo_ilo
        ])

        # Get list bobot PI
        list_pi_ilo = PerformanceIndicator.objects.filter(
            pi_area__ilo=ilo
        )
        list_bobot_pi_ilo = np.array([
            clo.get_pi_clo().count() / list_pi_ilo.count() for clo in list_clo_ilo
        ])

        # Get list nilai CLO peserta
        nilai_clo_peserta_qs = NilaiCloPeserta.objects.filter(
            peserta=peserta,
            clo__in=list_clo_ilo,
        ).values_list('nilai')
        list_nilai_clo_peserta = np.array(nilai_clo_peserta_qs).flatten()
        
        # Use try to prevent miss shape
        try:
            konversi_clo_to_ilo = bobot_mk * (list_persentase_clo * list_bobot_pi_ilo) * nilai_max
        except ValueError:
            if settings.DEBUG:
                print('Shape array tidak sama. Persentase CLO: {}, Bobot PI ILO: {}, Nilai CLO Peserta: {}'.format(
                    list_persentase_clo.shape, list_bobot_pi_ilo.shape, list_nilai_clo_peserta.shape))
            continue
        
        persentase_konversi = konversi_clo_to_ilo / np.sum(konversi_clo_to_ilo)
        
        # Use try to prevent miss shape
        try:
            persentase_capaian_ilo = persentase_konversi * list_nilai_clo_peserta
        except ValueError:
            if settings.DEBUG:
                print('Shape array tidak sama. Persentase Konversi: {}, Nilai CLO Peserta: {}'.format(
                    persentase_konversi.shape, list_nilai_clo_peserta.shape))
            continue

        persentase_capaian_ilo = np.sum(persentase_capaian_ilo)

        nilai_ilo_mhs_obj, _ = NilaiMataKuliahIloMahasiswa.objects.get_or_create(
            peserta=peserta,
            ilo=ilo
        )

        if nilai_ilo_mhs_obj.nilai_ilo is None:
            nilai_ilo_mhs_obj.nilai_ilo = persentase_capaian_ilo
            nilai_ilo_mhs_obj.save()
        else:
            if nilai_ilo_mhs_obj.nilai_ilo != persentase_capaian_ilo:
                nilai_ilo_mhs_obj.nilai_ilo = persentase_capaian_ilo
                nilai_ilo_mhs_obj.save()


def alphabet_to_number(alphabet):
    """
    Change alphabet to number
    >>> alphabe_to_number('z')
    26
    """
    list_alphabet = list('abcdefghijklmnopqrstuvwxyz')
    return [i for i, huruf in enumerate(list_alphabet) if huruf == alphabet.lower()][0] + 1


def number_to_alphabet(number):
    """
    Change number to alphabet
    >>> number_to_alphabet(26)
    'z'
    """
    list_alphabet = list('abcdefghijklmnopqrstuvwxyz')
    return list_alphabet[number-1]


def add_border_to_merged_cells(merged_cells, border):
    """Add border to merged cells

    Args:
        merged_cells (_type_): Merged cells
        border (Border): Border to apply
    """
    
    for cells in merged_cells:
        for cell in cells:
            cell.border = border


def make_cell_title_style(cell):
    """Make cell style with title style, Boild and center alignment

    Args:
        cell (Cell): Target cell
    """

    bold_font = Font(bold=True)
    center_align = Alignment(horizontal='center', vertical='center')

    cell.font = bold_font
    cell.alignment = center_align


def stretch_cell_width(worksheet, column, column_letter):
    """Stretch cell width according to max width

    Args:
        worksheet (WorkSheet): Worksheet
        column (Column): Worksheet column
        column_letter (str): Column letter
    """

    max_width = 10

    for cell in column:
        if not cell.value: continue
        max_width = max((max_width, len(str(cell.value))))

    worksheet.column_dimensions[column_letter].width = max_width + 2


def lock_or_unlock_cells(cells_by_row, protection):
    """Lock or unlock cells

    Args:
        cells_by_row (list): Range Cells
        protection (Protection): Protection
    """
    
    for cells in cells_by_row:
        for cell in cells:
            cell.protection = protection


def generate_template_nilai_mk_semester(mk_semester: MataKuliahSemester, list_peserta_mk: QuerySet[PesertaMataKuliah]):
    workbook = openpyxl.Workbook()
    worksheet: Worksheet  = workbook.active

    # Worksheet properties
    all_side_border = Border(
        left=Side(style='thin'), 
        right=Side(style='thin'), 
        top=Side(style='thin'), 
        bottom=Side(style='thin')
    )
    center_align = Alignment(horizontal='center', vertical='center')

    title = 'UNIVERSITAS HASANUDDIN'
    DETAIL = {
        'Fakultas': mk_semester.mk_kurikulum.kurikulum.prodi_jenjang.program_studi.fakultas.nama,
        'Program Studi': mk_semester.mk_kurikulum.kurikulum.prodi_jenjang.program_studi.nama,
        'Jenjang Prodi': mk_semester.mk_kurikulum.kurikulum.prodi_jenjang.jenjang_studi.kode,
        'Semester': mk_semester.semester.semester.nama,
        'Kode Mata Kuliah': mk_semester.mk_kurikulum.kode,
        'Nama Mata Kuliah': mk_semester.mk_kurikulum.nama,
        'Unique ID': '{}/{}'.format(mk_semester.semester.pk, mk_semester.pk)
    }

    # Title
    worksheet.merge_cells('B1:H1')
    title_cell = worksheet['B1']
    
    title_cell.value = title
    make_cell_title_style(title_cell)

    # Height and width
    # 50 = 100px
    worksheet.row_dimensions[1].height = 50
    # 2 because it is what it is
    worksheet.column_dimensions['B'].width = len(title) + 2
    
    # Detail
    start_col = 'B'
    start_row_clo = 3
    for key, value in DETAIL.items():
        # Merge cells
        merged_cells = 'C{0}:H{0}'.format(start_row_clo)
        worksheet.merge_cells(merged_cells)

        # Column B
        cell = '{}{}'.format(start_col, start_row_clo)
        worksheet[cell] = key
        worksheet[cell].border = all_side_border

        # Column C
        cell = '{}{}'.format('C', start_row_clo)
        worksheet[cell] = value
        # Add border to merged cell
        add_border_to_merged_cells(worksheet[merged_cells], all_side_border)

        start_row_clo += 1
    
    # Catatan
    CATATAN = (
        '*User hanya bisa menambah, mengubah, dan menghapus nilai per Komponen dalam Sheet ini.',
        '*Disarankan untuk tidak mengubah "Unique ID" untuk meminimalisir kesalahan baca oleh sistem.',
        '*Disarankan untuk tidak membuka kunci Sheet untuk meminimalisir kesalahan baca oleh sistem.',
        '*Jika ingin menambah, menghapus, atau mengubah peserta, disarankan untuk mengubah dari sistemnya.',
    )
    start_col = 'B'
    end_col = 'H'
    start_col_num = alphabet_to_number(start_col)
    start_row = 11

    for i, note in enumerate(CATATAN, 1):
        merged_cells = '{0}{1}:{2}{1}'.format(start_col, start_row, end_col)
        worksheet.merge_cells(merged_cells)

        worksheet['{}{}'.format(start_col, start_row)] = note
        # +1 is next row
        start_row += 1

    # List mahasiswa dan nilai
    # Header
    HEADER_TITLES = ('No.', 'NIM', 'Nama')
    start_col = 'A'
    start_col_num = alphabet_to_number(start_col)
    start_row = 16
    end_row = 18

    for i, title in enumerate(HEADER_TITLES, 1):
        merged_cells = '{0}{1}:{0}{2}'.format(start_col, start_row, end_row)
        worksheet.merge_cells(merged_cells)

        # Title
        title_cell = '{}{}'.format(start_col, start_row)
        worksheet[title_cell] = title
        make_cell_title_style(worksheet[title_cell])
        add_border_to_merged_cells(worksheet[merged_cells], all_side_border)

        start_col = number_to_alphabet(start_col_num + i)

    # List CLO
    start_col = 'D'
    start_row_clo = 16
    start_row_komponen = 17
    start_row_persentase = 18

    list_clo: QuerySet[Clo] = mk_semester.get_all_clo()

    for clo in list_clo:
        start_col_num = alphabet_to_number(start_col)
        list_komponen: QuerySet[KomponenClo] = clo.get_komponen_clo()

        # Nama CLO
        # Merged cells
        if list_komponen.count() > 1:
            # -1 is start column itself
            end_col_num = start_col_num + len(list_komponen) - 1
            end_col = number_to_alphabet(end_col_num)
            
            merged_cells = '{0}{1}:{2}{1}'.format(start_col, start_row_clo, end_col)
            worksheet.merge_cells(merged_cells)
            add_border_to_merged_cells(worksheet[merged_cells], all_side_border)
        
        # Nama CLO
        cell = '{}{}'.format(start_col, start_row_clo)
        worksheet[cell] = clo.nama
        worksheet[cell].border = all_side_border
        make_cell_title_style(worksheet[cell])

        # Komponen CLO
        for komponen in list_komponen:
            column = number_to_alphabet(start_col_num)

            # Nama Komponen
            cell = '{}{}'.format(column, start_row_komponen)
            worksheet[cell] = komponen.instrumen_penilaian
            worksheet[cell].border = all_side_border
            make_cell_title_style(worksheet[cell])

            # Persentase Komponen
            cell = '{}{}'.format(column, start_row_persentase) 
            worksheet[cell] = komponen.persentase/100
            worksheet[cell].style = 'Percent'
            worksheet[cell].border = all_side_border
            make_cell_title_style(worksheet[cell])

            stretch_cell_width(worksheet, worksheet[column], column)

            # +1 is next column
            start_col_num += 1
        
        start_col = number_to_alphabet(start_col_num)

    # Set end column to add border
    end_col = column

    # List Mahasiswa
    start_row = 19

    for i, peserta_mk in enumerate(list_peserta_mk, 1):
        # Nomor
        cell = 'A{}'.format(start_row)
        worksheet[cell] = i
        worksheet[cell].alignment = center_align

        # NIM
        worksheet['B{}'.format(start_row)] = peserta_mk.mahasiswa.username
        # Nama
        worksheet['C{}'.format(start_row)] = peserta_mk.mahasiswa.nama

        start_row += 1

    end_row = start_row - 1
    add_border_to_merged_cells(worksheet['A19:{}{}'.format(end_col, end_row)], all_side_border)
    stretch_cell_width(worksheet, worksheet['C'], 'C')

    # Lock cells
    nilai_protection = Protection(locked=False, hidden=False)
    nilai_cells = 'D14:{}{}'.format(end_col, end_row)
    lock_or_unlock_cells(worksheet[nilai_cells], nilai_protection)
    worksheet.protection.enable()
    
    # Save the workbook to a BytesIO object
    file_stream = BytesIO()
    workbook.save(file_stream)

    file_stream.seek(0)

    return file_stream
