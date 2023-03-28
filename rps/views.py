from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import TemplateView
from accounts.enums import RoleChoices
from learning_outcomes_assessment.forms.edit import MultiFormView
from ilo.models import Ilo
from mata_kuliah_semester.models import MataKuliahSemester
from rps.models import RencanaPembelajaranSemester
from accounts.utils import get_user_profile
from .models import (
    RencanaPembelajaranSemester,
    PengembangRPS,
    KoordinatorRPS,
    DosenPengampuRPS,
    MataKuliahSyaratRPS,
    PertemuanRPS,
    PembelajaranPertemuanRPS,
    DurasiPertemuanRPS,
    JenisPertemuan,
    TipeDurasi,
)
from .forms import (
    KaprodiRPSForm,
    RencanaPembelajaranSemesterForm,
    PengembangRPSForm,
    KoordinatorRPSForm,
    DosenPengampuRPSForm,
    MataKuliahSyaratRPSForm,
)


# Create your views here.
class RPSHomeView(TemplateView):
    template_name = 'rps/home.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
    
    @property
    def get_ilo(self):
        ilo_qs = Ilo.objects.filter(
            pi_area__performanceindicator__piclo__clo__mk_semester=self.mk_semester_obj
        ).distinct()

        return ilo_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        is_rincian_tab = True
        is_pertemuan_tab = False
        
        rps: RencanaPembelajaranSemester = None
        if hasattr(self.mk_semester_obj, 'rencanapembelajaransemester'):
            rps = self.mk_semester_obj.rencanapembelajaransemester

        context.update({
            'mk_semester_obj': self.mk_semester_obj,
            'is_rincian_tab': is_rincian_tab,
            'is_pertemuan_tab': is_pertemuan_tab,
            'ilo_object_list': self.get_ilo,
            'rps': rps,
        })
        return context


class RPSCreateView(MultiFormView):
    form_classes = {
        'kaprodi_rps_form': KaprodiRPSForm,
        'rps_form': RencanaPembelajaranSemesterForm,
        'pengembang_rps_form': PengembangRPSForm,
        'koordinator_rps_form': KoordinatorRPSForm,
        'dosen_pengampu_rps_form': DosenPengampuRPSForm,
        'mata_kuliah_syarat_rps_form': MataKuliahSyaratRPSForm,
    }
    template_name = 'rps/create-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.success_url = self.mk_semester_obj.get_rps_home_url()

    def dispatch(self, request, *args, **kwargs):
        if hasattr(self.mk_semester_obj, 'rencanapembelajaransemester'):
            messages.warning(request, 'Rencana Pembelajaran Semester untuk mata kuliah ini sudah ada.')
            return redirect(self.success_url)
        
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['mata_kuliah_syarat_rps_form'].update({
            'current_mk_semester': self.mk_semester_obj
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
        })
        return context
    
    def get_dosen_profile(self, list_nip: list):
        list_dosen_profile = []
        for nip in list_nip:
            dosen_user_profile = get_user_profile(
                user={
                    'username': nip
                },
                role=RoleChoices.DOSEN
            )
            # Skip dosen user profile is it is none
            if dosen_user_profile is None:
                messages.error(self.request, 'Profil dosen dengan NIP: {} tidak ada di Neosia.'.format(nip))
                continue

            list_dosen_profile.append(dosen_user_profile)
        return list_dosen_profile
    
    def save_dosen_rps_form(self, model, form_cleaned_data, field_key: str, rps_obj: RencanaPembelajaranSemester):
        list_dosen_profile = self.get_dosen_profile(form_cleaned_data[field_key])
        for dosen_profile in list_dosen_profile:
            dosen_user = authenticate(self.request, user=dosen_profile, role=RoleChoices.DOSEN)
            model.objects.create(
                rps=rps_obj,
                dosen=dosen_user,
            )
    
    def forms_valid(self, forms: dict) -> HttpResponse:
        cleaned_data = {}

        for key, form in forms.items():
            cleaned_data[key] = form.cleaned_data

        # Kaprodi
        kaprodi_rps_form = cleaned_data['kaprodi_rps_form']
        kaprodi_user_profile = self.get_dosen_profile(list_nip=[kaprodi_rps_form['kaprodi']])

        if len(kaprodi_user_profile) > 0:
            kaprodi_user_profile = kaprodi_user_profile[0]
        else:
            messages.error(self.request, 'Data Kepala Program Studi tidak bisa didapatkan.')
            return redirect(self.success_url)
        
        kaprodi_user = authenticate(self.request, user=kaprodi_user_profile, role=RoleChoices.DOSEN)
        
        # RPS
        rps_form = cleaned_data['rps_form']
        rps_obj = RencanaPembelajaranSemester.objects.create(
            mk_semester=self.mk_semester_obj,
            kaprodi=kaprodi_user,
            **rps_form
        )

        # Dosen pengembang RPS
        pengembang_rps_form = cleaned_data['pengembang_rps_form']
        self.save_dosen_rps_form(PengembangRPS, pengembang_rps_form, 'dosen_pengembang', rps_obj)

        # Dosen Koordinator RPS
        koordinator_rps_form = cleaned_data['koordinator_rps_form']
        self.save_dosen_rps_form(KoordinatorRPS, koordinator_rps_form, 'dosen_koordinator', rps_obj)

        # Dosen Pengampu RPS
        dosen_pengampu_rps_form = cleaned_data['dosen_pengampu_rps_form']
        self.save_dosen_rps_form(DosenPengampuRPS, dosen_pengampu_rps_form, 'dosen_pengampu', rps_obj)

        # Mata Kuliah Syarat
        mata_kuliah_syarat_rps_form = cleaned_data['mata_kuliah_syarat_rps_form']
        for mk_semester_id in mata_kuliah_syarat_rps_form['mk_semester_syarat']:
            try:
                mk_semester_obj = MataKuliahSemester.objects.get(id=mk_semester_id)
            except (MataKuliahSemester.DoesNotExist, MataKuliahSemester.MultipleObjectsReturned):
                message = 'Tidak bisa mendapatkan mata kuliah semester dengan ID: {}'.format(mk_semester_id)
                if settings.DEBUG: print(message)
                messages.error(self.request, message)

                continue

            MataKuliahSyaratRPS.objects.create(
                rps=rps_obj,
                mk_semester=mk_semester_obj,
            )

        messages.success(self.request, 'Proses penambahan rincian RPS sudah selesai.')
        
        return super().form_valid(forms)
