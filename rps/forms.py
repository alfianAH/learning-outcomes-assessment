from django import forms
from django.db.models import QuerySet
from django.forms import inlineformset_factory
from learning_outcomes_assessment.widgets import (
    MyRadioInput,
    MySelectInput,
    PagedownWidget,
    MyNumberInput,
    MyTextareaInput,
)
from learning_outcomes_assessment.forms.formset import CanDeleteInlineFormSet
from mata_kuliah_semester.models import MataKuliahSemester
from mata_kuliah_kurikulum.models import MataKuliahKurikulum
from clo.models import Clo
from .models import(
    RencanaPembelajaranSemester,
    PertemuanRPS,
    RincianPertemuanRPS,
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


class SKSForm(forms.Form):
    teori_sks = forms.IntegerField(
        min_value=0,
        required=True,
        widget=MyNumberInput(attrs={
            'placeholder': 2
        }),
        label='Teori',
    )
    praktik_sks = forms.IntegerField(
        min_value=0,
        required=True,
        widget=MyNumberInput(attrs={
            'placeholder': 1
        }),
        label='Praktik',
    )

    def __init__(self, mk_kurikulum: MataKuliahKurikulum, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mk_kurikulum = mk_kurikulum

        self.fields['teori_sks'].help_text = 'SKS untuk Teori. SKS MK: {}'.format(self.mk_kurikulum.sks)
        self.fields['praktik_sks'].help_text = 'SKS untuk Praktik. SKS MK: {}'.format(self.mk_kurikulum.sks)

    def clean(self):
        cleaned_data = super().clean()
        teori_sks = cleaned_data['teori_sks']
        praktik_sks = cleaned_data['praktik_sks']

        total_sks = teori_sks + praktik_sks
        if total_sks > self.mk_kurikulum.sks:
            self.add_error('teori_sks', 'Total SKS teori dan praktik tidak sesuai dengan jumlah SKS di database. Input: {}, Ekspektasi: {}'.format(total_sks, self.mk_kurikulum.sks))
        
        return cleaned_data


class RencanaPembelajaranSemesterForm(forms.ModelForm):
    class Meta:
        model = RencanaPembelajaranSemester
        fields = '__all__'
        exclude = ['mk_semester', 'created_date', 'kaprodi', 'lock']
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
            'materi_pembelajaran': PagedownWidget(),
            'pustaka_utama': PagedownWidget(),
            'pustaka_pendukung': PagedownWidget(),
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
        label='Mata Kuliah Syarat',
        required=False,
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


class RincianRPSDuplicateForm(forms.Form):
    semester = forms.ChoiceField(
        widget=MyRadioInput(),
        label='Duplikasi Rincian RPS',
    )

    def __init__(self, mk_semester: MataKuliahSemester, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['semester'].help_text = 'Berikut adalah pilihan semester dari <b>{}</b>. Pilih salah satu semester untuk menduplikasi Rincian RPS dari semester tersebut ke <b>{}</b>'.format(mk_semester.mk_kurikulum.kurikulum.nama, mk_semester.semester.semester.nama)

        self.fields['semester'].choices = choices


class PertemuanRPSForm(forms.ModelForm):
    class Meta:
        model = PertemuanRPS
        fields = '__all__'
        exclude = ['mk_semester', 'lock']
        labels = {
            'clo': 'CLO',
            'bobot_penilaian': 'Bobot penilaian (%)',
            'pertemuan_awal': 'Awal',
            'pertemuan_akhir': 'Akhir (opsional)',
            'tipe_pertemuan': 'Tipe pertemuan',
        }
        help_texts = {
            'pertemuan_awal': 'Range pertemuan. Contoh: Pertemuan 1-3, maka awal = 1, akhir = 3.',
            'pertemuan_akhir': 'Range pertemuan. Contoh: Pertemuan 1-3, maka awal = 1, akhir = 3.',
            'clo': 'Pilih CLO yang berkaitan dengan pertemuan untuk menentukan bobot penilaian.',
            'bobot_penilaian': 'Bobot penilaian pertemuan dari persentase CLO yang dipilih.',
            'tipe_pertemuan': 'Silakan memilih antara pertemuan biasa (reguler) atau pertemuan ujian (ujian mid atau final).'
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
                'class': 'w-full',
            }),
            'pertemuan_akhir': MyNumberInput(attrs={
                'placeholder': 3,
                'min': 0,
                'class': 'w-full',
            }),
            'tipe_pertemuan': MySelectInput(),
        }
    
    def __init__(self, clo_qs: QuerySet[Clo], pertemuan_rps_qs: QuerySet[PertemuanRPS], current_pertemuan_rps: PertemuanRPS = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['clo'].queryset = clo_qs
        self.pertemuan_rps_qs = pertemuan_rps_qs
        self.current_pertemuan_rps = current_pertemuan_rps

    def clean(self):
        cleaned_data = super().clean()
        clo: Clo = cleaned_data.get('clo')

        list_pertemuan_db = []
        if self.current_pertemuan_rps is not None:
            self.pertemuan_rps_qs = self.pertemuan_rps_qs.exclude(id=self.current_pertemuan_rps.pk)
        
        for pertemuan_rps in self.pertemuan_rps_qs:
            # List pertemuan in database
            pertemuan_awal_db = pertemuan_rps.pertemuan_awal
            pertemuan_akhir_db = pertemuan_rps.pertemuan_akhir

            if pertemuan_akhir_db is None:
                list_pertemuan_db.append(pertemuan_awal_db)
            else:
                for i in range(pertemuan_awal_db, pertemuan_akhir_db + 1):
                    list_pertemuan_db.append(i)

        list_pertemuan_db = list(set(list_pertemuan_db))
        # Check pertemuan
        pertemuan_awal = cleaned_data.get('pertemuan_awal')
        pertemuan_akhir = cleaned_data.get('pertemuan_akhir')
        
        # List pertemuan in input
        list_pertemuan = []
        if pertemuan_akhir is None:
            list_pertemuan.append(pertemuan_awal)
        else:
            if pertemuan_akhir < pertemuan_awal:
                self.add_error('pertemuan_akhir', 'Pertemuan akhir harus lebih besar dari pertemuan awal')
            for i in range(pertemuan_awal, pertemuan_akhir + 1):
                list_pertemuan.append(i)
        
        listed_pertemuan_in_db = [pertemuan for pertemuan in list_pertemuan if pertemuan in list_pertemuan_db]
        if len(listed_pertemuan_in_db) > 0:
            self.add_error('pertemuan_awal', 'Pertemuan {} sudah ada di database.'.format(listed_pertemuan_in_db))  

        # Check bobot penilaian
        # Pertemuan RPS in database
        pertemuan_rps_clo_qs = self.pertemuan_rps_qs.filter(
            clo=clo
        )
        bobot_penilaian = cleaned_data.get('bobot_penilaian')
        total_bobot_penilaian_clo = sum([pertemuan_rps.bobot_penilaian for pertemuan_rps in pertemuan_rps_clo_qs])
        total_persentase_clo = clo.get_total_persentase_komponen()

        current_total_bobot_penilaian_clo = total_bobot_penilaian_clo + bobot_penilaian

        if current_total_bobot_penilaian_clo > total_persentase_clo:
            self.add_error('bobot_penilaian', 'Bobot penilaian untuk {} berlebihan. Persentase CLO: {}, Total bobot penilaian CLO saat ini: {}'.format(clo.nama, total_persentase_clo, current_total_bobot_penilaian_clo))
        
        return cleaned_data
    

class RincianPertemuanRPSForm(forms.ModelForm):
    class Meta:
        model = RincianPertemuanRPS
        fields = '__all__'
        exclude = ['pertemuan_rps', 'lock']
        labels = {
            'learning_outcome': 'Capaian pembelajaran',
            'indikator': 'Indikator',
            'bentuk_kriteria': 'Bentuk dan kriteria',
            'materi_pembelajaran': 'Materi pembelajaran',
        }
        widgets = {
            'learning_outcome': MyTextareaInput(attrs={
                'rows': 3,
                'placeholder': 'Masukkan kemampuan akhir tiap tahapan pembelajaran.'
            }),
            'indikator': PagedownWidget(),
            'bentuk_kriteria': PagedownWidget(),
            'materi_pembelajaran': PagedownWidget(),
        }


class PertemuanLuringForm():
    jenis_pertemuan = forms.Field(
        widget=forms.HiddenInput(),
        initial=JenisPertemuan.OFFLINE,
    )


class PertemuanDaringForm():
    jenis_pertemuan = forms.Field(
        widget=forms.HiddenInput(),
        initial=JenisPertemuan.ONLINE,
    )


class PembelajaranPertemuanRPSForm(forms.ModelForm):
    class Meta:
        model = PembelajaranPertemuanRPS
        fields = '__all__'
        exclude = ['pertemuan_rps', 'lock']
        widgets = {
            'bentuk_pembelajaran': PagedownWidget(),
            'metode_pembelajaran': PagedownWidget(),
        }


class PembelajaranPertemuanLuringRPSForm(PertemuanLuringForm, PembelajaranPertemuanRPSForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['jenis_pertemuan'].initial = JenisPertemuan.OFFLINE
        self.fields['bentuk_pembelajaran'].label = 'Luring (offline)'
        self.fields['metode_pembelajaran'].label = 'Luring (offline)'

    def add_prefix(self, field_name: str) -> str:
        return '{}_pembelajaran_luring'.format(super().add_prefix(field_name))


class PembelajaranPertemuanDaringRPSForm(PertemuanDaringForm, PembelajaranPertemuanRPSForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['jenis_pertemuan'].initial = JenisPertemuan.ONLINE
        self.fields['bentuk_pembelajaran'].label = 'Daring (online)'
        self.fields['metode_pembelajaran'].label = 'Daring (online)'
    
    def add_prefix(self, field_name: str) -> str:
        return '{}_pembelajaran_daring'.format(super().add_prefix(field_name))


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
        exclude = ['pertemuan_rps', 'lock']
        labels = {
            'pengali_durasi': 'banyak',
            'durasi_menit': 'menit',
        }
        widgets = {
            'pengali_durasi': MyNumberInput(attrs={
                'placeholder': 2,
                'min': 0,
                'class': 'w-full',
            }),
            'durasi_menit': MyNumberInput(attrs={
                'placeholder': 45,
                'min': 0,
                'class': 'w-full',
            }),
        }


class DurasiPertemuanLuringRPSForm(PertemuanLuringForm, DurasiPertemuanRPSForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['jenis_pertemuan'].initial = JenisPertemuan.OFFLINE
    
    def add_prefix(self, field_name: str) -> str:
        return '{}_durasi_luring'.format(super().add_prefix(field_name))


class DurasiPertemuanDaringRPSForm(PertemuanDaringForm, DurasiPertemuanRPSForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['jenis_pertemuan'].initial = JenisPertemuan.ONLINE
    
    def add_prefix(self, field_name: str) -> str:
        return '{}_durasi_daring'.format(super().add_prefix(field_name))


DurasiPertemuanLuringRPSFormset = inlineformset_factory(
    PertemuanRPS,
    DurasiPertemuanRPS,
    form=DurasiPertemuanLuringRPSForm,
    formset=CanDeleteInlineFormSet,
    extra=1,
    can_delete=True,
)

DurasiPertemuanDaringRPSFormset = inlineformset_factory(
    PertemuanRPS,
    DurasiPertemuanRPS,
    form=DurasiPertemuanDaringRPSForm,
    formset=CanDeleteInlineFormSet,
    extra=1,
    can_delete=True,
)


class PertemuanRPSDuplicateForm(forms.Form):
    semester = forms.ChoiceField(
        widget=MyRadioInput(),
        label='Duplikasi Pertemuan RPS',
    )

    def __init__(self, mk_semester: MataKuliahSemester, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['semester'].help_text = 'Berikut adalah pilihan semester dari <b>{}</b>. Pilih salah satu semester untuk menduplikasi Pertemuan RPS dari semester tersebut ke <b>{}</b>'.format(mk_semester.mk_kurikulum.kurikulum.nama, mk_semester.semester.semester.nama)

        self.fields['semester'].choices = choices
