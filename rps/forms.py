from django import forms
from .models import(
    RencanaPembelajaranSemester,
    PengembangRPS,
    KoordinatorRPS,
    DosenPengampuRPS,
    MataKuliahSyaratRPS,
    PertemuanRPS,
    PembelajaranPertemuanRPS,
    DurasiPertemuanRPS,
    JenisPertemuan
)
from learning_outcomes_assessment.widgets import (
    MySelectInput,
    PagedownWidget,
    MyNumberInput,
    MyTextareaInput,
)


class RencanaPembelajaranSemesterForm(forms.ModelForm):
    class Meta:
        model = RencanaPembelajaranSemester
        fields = '__all__'
        exclude = ['mk_semester', 'created_date']
        labels = {
            'kaprodi': 'Kepala Program Studi',
            'semester': 'Semester',
            'deskripsi': 'Deskripsi singkat mata kuliah',
            'clo_details': 'Capaian Pembelajaran Mata Kuliah',
            'materi_pembelajaran': 'Materi pembelajaran',
            'pustaka_utama': 'Pustaka utama',
            'pustaka_pendukung': 'Pustaka pendukung',
        }
        help_texts = {
            'kaprodi': 'Pilih Kepala Program Studi saat ini',
            'semester': 'Semester di mana mata kuliah berada. Contoh: Semester 1, 2.',
        }
        widgets = {
            'kaprodi': MySelectInput(attrs={
                'class': 'single-select-search',
            }),
            'semester': MyNumberInput(),
            'deskripsi': MyTextareaInput(),
            'clo_details': MyTextareaInput(),
            'materi_pembelajaran': PagedownWidget(),
            'pustaka_utama': PagedownWidget(),
            'pustaka_pendukung': PagedownWidget(),
        }


class DosenRPSForm(forms.Form):
    dosen = forms.Field(
        widget=forms.SelectMultiple(attrs={
            'class': 'multi-select-search',
            'multiple': 'multiple'
        }),
    )


class PengembangRPSForm(DosenRPSForm):
    def __init__(self, *args, **kwargs):
        self.fields['dosen'].label = 'Pengembang RPS'


class KoordinatorRPSForm(DosenRPSForm):
    def __init__(self, *args, **kwargs):
        self.fields['dosen'].label = 'Koordinator Mata Kuliah'


class DosenPengampuRPSForm(DosenRPSForm):
    def __init__(self, *args, **kwargs):
        self.fields['dosen'].label = 'Dosen pengampu'


class MataKuliahSyaratRPSForm(forms.ModelForm):
    mk_semester = forms.ChoiceField(
        widget=forms.SelectMultiple(attrs={
            'class': 'multi-select-search',
            'multiple': 'multiple'
        }),
    )
