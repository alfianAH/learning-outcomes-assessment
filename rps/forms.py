from django import forms
from django.db.models import QuerySet
from django.forms import inlineformset_factory
from learning_outcomes_assessment.widgets import (
    MySelectInput,
    PagedownWidget,
    MyNumberInput,
    MyTextareaInput,
)
from mata_kuliah_semester.models import MataKuliahSemester
from .models import(
    RencanaPembelajaranSemester,
    PertemuanRPS,
    PembelajaranPertemuanRPS,
    DurasiPertemuanRPS,
    JenisPertemuan,
    TipeDurasi,
)


class KaprodiRPSForm(forms.Form):
    kaprodi = forms.Field(
        widget=MySelectInput(attrs={
            'class': 'select-search-dosen',
        }),
        label='Kepala Program Studi',
        help_text='Pilih Kepala Program Studi saat ini'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        kaprodi = kwargs.get('initial', {}).get('kaprodi')
        if kaprodi is None: return

        self.fields['kaprodi'].widget.choices = [(kaprodi.username, kaprodi.nama)]


class RencanaPembelajaranSemesterForm(forms.ModelForm):
    class Meta:
        model = RencanaPembelajaranSemester
        fields = '__all__'
        exclude = ['mk_semester', 'created_date', 'kaprodi']
        labels = {
            'semester': 'Semester',
            'deskripsi': 'Deskripsi singkat mata kuliah',
            'clo_details': 'Capaian Pembelajaran Mata Kuliah',
            'materi_pembelajaran': 'Materi pembelajaran',
            'pustaka_utama': 'Pustaka utama',
            'pustaka_pendukung': 'Pustaka pendukung',
        }
        help_texts = {
            'semester': 'Semester di mana mata kuliah berada. Contoh: Semester 1, 2.',
        }
        widgets = {
            'semester': MyNumberInput(attrs={
                'min': 0,
                'placeholder': '1, 2, 3, ...'
            }),
            'deskripsi': MyTextareaInput(attrs={
                'placeholder': 'Masukkan deskripsi singkat mata kuliah',
                'rows': 3,
            }),
            'clo_details': MyTextareaInput(attrs={
                'placeholder': 'Masukkan capaian pembelajaran dari mata kuliah',
                'rows': 3,
            }),
            'materi_pembelajaran': PagedownWidget(attrs={
                'rows': 3,
            }),
            'pustaka_utama': PagedownWidget(attrs={
                'rows': 3,
            }),
            'pustaka_pendukung': PagedownWidget(attrs={
                'rows': 3,
            }),
        }
    

class PengembangRPSForm(forms.Form):
    dosen_pengembang = forms.Field(
        widget=forms.SelectMultiple(attrs={
            'class': 'select-search-dosen',
            'multiple': 'multiple'
        }),
        label='Pengembang RPS'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        list_dosen_pengembang = kwargs.get('initial', {}).get('dosen_pengembang')
        if list_dosen_pengembang is None: return

        self.fields['dosen_pengembang'].widget.choices = [(dosen.username, dosen.nama) for dosen in list_dosen_pengembang]
        self.fields['dosen_pengembang'].initial = [dosen.username for dosen in list_dosen_pengembang]


class KoordinatorRPSForm(forms.Form):
    dosen_koordinator = forms.Field(
        widget=forms.SelectMultiple(attrs={
            'class': 'select-search-dosen',
            'multiple': 'multiple'
        }),
        label='Koordinator Mata Kuliah'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        list_dosen_koordinator = kwargs.get('initial', {}).get('dosen_koordinator')
        if list_dosen_koordinator is None: return

        self.fields['dosen_koordinator'].widget.choices = [(dosen.username, dosen.nama) for dosen in list_dosen_koordinator]
        self.fields['dosen_koordinator'].initial = [dosen.username for dosen in list_dosen_koordinator]


class DosenPengampuRPSForm(forms.Form):
    dosen_pengampu = forms.Field(
        widget=forms.SelectMultiple(attrs={
            'class': 'select-search-dosen',
            'multiple': 'multiple'
        }),
        label='Dosen pengampu'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        list_dosen_pengampu = kwargs.get('initial', {}).get('dosen_pengampu')
        if list_dosen_pengampu is None: return

        self.fields['dosen_pengampu'].widget.choices = [(dosen.username, dosen.nama) for dosen in list_dosen_pengampu]
        self.fields['dosen_pengampu'].initial = [dosen.username for dosen in list_dosen_pengampu]


class MataKuliahSyaratRPSForm(forms.Form):
    mk_semester_syarat = forms.Field(
        widget=forms.SelectMultiple(attrs={
            'class': 'multi-select-search-mk-semester',
            'multiple': 'multiple'
        }),
        label='Mata Kuliah Syarat'
    )

    def __init__(self, current_mk_semester: MataKuliahSemester, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = []
        list_mk_semester: QuerySet[MataKuliahSemester] = current_mk_semester.semester.get_mk_semester()
        
        for mk_semester in list_mk_semester:
            if mk_semester == current_mk_semester: continue
            choices.append((mk_semester.pk, mk_semester.mk_kurikulum.nama))

        self.fields['mk_semester_syarat'].widget.choices = choices
        
        list_mk_syarat = kwargs.get('initial', {}).get('mk_semester_syarat')
        if list_mk_syarat is None: return
        
        self.fields['mk_semester_syarat'].initial = [str(mk_semester.pk) for mk_semester in list_mk_syarat]


class PertemuanRPSForm(forms.ModelForm):
    class Meta:
        model = PertemuanRPS
        fields = '__all__'
        exclude = ['rps']
        labels = {
            'clo': 'CLO',
            'bobot_penilaian': 'Bobot penilaian (%)',
            'pertemuan_awal': 'Awal',
            'pertemuan_akhir': 'Akhir (opsional)',
            'learning_outcome': 'Capaian pembelajaran',
            'indikator': 'Indikator',
            'bentuk_kriteria': 'Bentuk dan kriteria',
            'materi_pembelajaran': 'Materi pembelajaran',
        }
        help_texts = {
            'pertemuan_awal': 'Range pertemuan. Contoh: Pertemuan 1-3, maka awal = 1, akhir = 3.',
            'pertemuan_akhir': 'Range pertemuan. Contoh: Pertemuan 1-3, maka awal = 1, akhir = 3.',
            'clo': 'Pilih CLO yang berkaitan dengan pertemuan untuk menentukan bobot penilaian.',
            'bobot_penilaian': 'Bobot penilaian pertemuan dari persentase CLO yang dipilih.',
        }
        widgets = {
            'clo': MySelectInput(attrs={
                'placeholder': 'Pilih CLO'
            }),
            'bobot_penilaian': MyNumberInput(attrs={
                'placeholder': 5
            }),
            'pertemuan_awal': MyNumberInput(attrs={
                'placeholder': 1,
                'min': 0,
            }),
            'pertemuan_akhir': MyNumberInput(attrs={
                'placeholder': 3,
                'min': 0,
            }),
            'learning_outcome': MyTextareaInput(attrs={
                'rows': 3,
                'placeholder': 'Masukkan kemampuan akhir tiap tahapan pembelajaran.'
            }),
            'indikator': PagedownWidget(attrs={
                'rows': 3,
            }),
            'bentuk_kriteria': PagedownWidget(attrs={
                'rows': 3,
            }),
            'materi_pembelajaran': PagedownWidget(attrs={
                'rows': 3,
            }),
        }


class PertemuanLuringForm():
    jenis_pertemuan = forms.HiddenInput(attrs={
        'value': JenisPertemuan.OFFLINE
    })


class PertemuanDaringForm():
    jenis_pertemuan = forms.HiddenInput(attrs={
        'value': JenisPertemuan.ONLINE
    })


class PembelajaranPertemuanRPSForm(forms.ModelForm):
    class Meta:
        model = PembelajaranPertemuanRPS
        fields = '__all__'
        exclude = ['pertemuan_rps']
        widget = {
            'bentuk_pembelajaran': PagedownWidget(attrs={
                'rows': 3,
            }),
            'metode_pembelajaran': PagedownWidget(attrs={
                'rows': 3,
            }),
        }


class PembelajaranPertemuanLuringRPSForm(PertemuanLuringForm, PembelajaranPertemuanRPSForm):
    pass


class PembelajaranPertemuanDaringRPSForm(PertemuanDaringForm, PembelajaranPertemuanRPSForm):
    pass


class DurasiPertemuanRPSForm(forms.ModelForm):
    tipe_durasi = forms.Field(
        widget=MySelectInput(
            attrs={
                'class': 'tipe-durasi-search',
            },
            choices=TipeDurasi.choices
        )
    )
    class Meta:
        model = DurasiPertemuanRPS
        fields = '__all__'
        exclude = ['pertemuan_rps']
        labels = {
            'pengali_durasi': 'banyak',
            'durasi_menit': 'menit',
        }
        widgets = {
            'pengali_durasi': MyNumberInput(attrs={
                'placeholder': 2,
                'min': 0,
            }),
            'durasi_menit': MyNumberInput(attrs={
                'placeholder': 45,
                'min': 0,
                'max': 60,
            }),
        }


class DurasiPertemuanLuringRPSForm(PertemuanLuringForm, DurasiPertemuanRPSForm):
    pass


class DurasiPertemuanDaringRPSForm(PertemuanDaringForm, DurasiPertemuanRPSForm):
    pass
