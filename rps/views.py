import json
from django.db.models import QuerySet
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import authenticate
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.base import RedirectView
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.views.generic.detail import DetailView
from accounts.enums import RoleChoices
from learning_outcomes_assessment.forms.edit import (
    MultiFormView,
    MultiModelFormView,
)
from learning_outcomes_assessment.list_view.views import DetailWithListViewModelA
from learning_outcomes_assessment.forms.edit import (
    ModelBulkDeleteView,
    DuplicateFormview,
)
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
    RincianPertemuanRPS,
    PembelajaranPertemuanRPS,
    DurasiPertemuanRPS,
    JenisPertemuan,
    TipeDurasi,
)
from .forms import (
    SKSForm,
    KaprodiRPSForm,
    RencanaPembelajaranSemesterForm,
    PengembangRPSForm,
    KoordinatorRPSForm,
    DosenPengampuRPSForm,
    MataKuliahSyaratRPSForm,
    PertemuanRPSForm,
    RincianPertemuanRPSForm,
    PembelajaranPertemuanLuringRPSForm,
    PembelajaranPertemuanDaringRPSForm,
    DurasiPertemuanLuringRPSFormset,
    DurasiPertemuanDaringRPSFormset,
    RincianRPSDuplicateForm,
    PertemuanRPSDuplicateForm,
)

from .utils import(
    get_semester_choices_rincian_rps_duplicate,
    duplicate_rincian_rps,
    get_semester_choices_pertemuan_rps_duplicate,
    duplicate_pertemuan_rps,
)


# Create your views here.
class RPSHomeView(DetailWithListViewModelA):
    template_name = 'rps/home.html'

    single_model = MataKuliahSemester
    single_pk_url_kwarg = 'mk_semester_id'
    single_object: MataKuliahSemester = None
    
    model = PertemuanRPS
    ordering = 'pertemuan_awal'

    bulk_delete_url: str = ''
    list_prefix_id = 'pertemuan-rps-'
    input_name = 'id_pertemuan_rps'
    list_id = 'pertemuan-rps-list-content'
    badge_template: str = 'rps/partials/pertemuan/badge-template-pertemuan-rps.html'
    list_item_name: str = 'rps/partials/pertemuan/list-item-name-pertemuan-rps.html'
    list_custom_field_template: str = 'rps/partials/pertemuan/list-custom-field-pertemuan-rps.html'
    table_custom_field_header_template: str = 'rps/partials/pertemuan/table-custom-field-header-pertemuan-rps.html'
    table_custom_field_template: str = 'rps/partials/pertemuan/table-custom-field-pertemuan-rps.html'
    table_footer_custom_field_template: str = 'rps/partials/pertemuan/table-footer-custom-field-pertemuan-rps.html'
    
    @property
    def get_ilo(self):
        ilo_qs = Ilo.objects.filter(
            pi_area__performanceindicator__piclo__clo__mk_semester=self.single_object
        ).distinct()

        return ilo_qs
    
    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.bulk_delete_url = self.single_object.get_pertemuan_rps_bulk_delete_url()
    
    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            mk_semester=self.single_object
        )
        return super().get_queryset()
    
    def total_bobot_penilaian_json(self):
        json_response = {}
        total_bobot_penilaian = self.single_object.get_total_bobot_penilaian_pertemuan_rps
        
        if total_bobot_penilaian > 100:
            total_exceed = total_bobot_penilaian - 100

            json_response.update({
                'labels': [
                    'Persentase berlebihan',
                    'Persentase bobot penilaian saat ini',
                ],
                'datasets': {
                    'data': [
                        total_exceed,
                        total_bobot_penilaian - total_exceed
                    ],
                    'backgroundColor': [
                        '#f43f5e',  # Rose 500
                        '#10b981',  # Emerald 500
                    ]
                }
            })
        elif total_bobot_penilaian == 100:
            json_response.update({
                'labels': [
                    'Persentase bobot penilaian saat ini',
                ],
                'datasets': {
                    'data': [
                        total_bobot_penilaian
                    ],
                    'backgroundColor': [
                        '#10b981',  # Emerald 500
                    ]
                }
            })
        else:
            json_response.update({
                'labels': [
                    'Persentase bobot penilaian saat ini',
                    'Kosong',
                ],
                'datasets': {
                    'data': [
                        total_bobot_penilaian,
                        100 - total_bobot_penilaian,
                    ],
                    'backgroundColor': [
                        '#10b981',  # Emerald 500
                        '#dcfce7',  # Emerald 100
                    ]
                }
            })

        return json.dumps(json_response)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_request = self.request.GET

        if get_request.get('active_tab') == 'pertemuan':
            context['is_pertemuan_tab'] = True
        
        rps: RencanaPembelajaranSemester = None
        if hasattr(self.single_object, 'rencanapembelajaransemester'):
            rps = self.single_object.rencanapembelajaransemester

        context.update({
            'ilo_object_list': self.get_ilo,
            'rps': rps,
            'total_bobot_penilaian_json': self.total_bobot_penilaian_json()
        })
        return context
    

class RPSFormView(MultiFormView):
    form_classes = {
        'sks_form': SKSForm,
        'kaprodi_rps_form': KaprodiRPSForm,
        'rps_form': RencanaPembelajaranSemesterForm,
        'pengembang_rps_form': PengembangRPSForm,
        'koordinator_rps_form': KoordinatorRPSForm,
        'dosen_pengampu_rps_form': DosenPengampuRPSForm,
        'mata_kuliah_syarat_rps_form': MataKuliahSyaratRPSForm,
    }

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.success_url = self.mk_semester_obj.get_rps_home_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['mata_kuliah_syarat_rps_form'].update({
            'current_mk_semester': self.mk_semester_obj
        })
        kwargs['sks_form'].update({
            'mk_kurikulum': self.mk_semester_obj.mk_kurikulum
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


class RPSCreateView(RPSFormView):
    template_name = 'rps/create-view.html'

    def dispatch(self, request, *args, **kwargs):
        if hasattr(self.mk_semester_obj, 'rencanapembelajaransemester'):
            messages.warning(request, 'Rencana Pembelajaran Semester untuk mata kuliah ini sudah ada.')
            return redirect(self.success_url)
        
        return super().dispatch(request, *args, **kwargs)
    
    def create_dosen_rps_form(self, model, form_cleaned_data, field_key: str, rps_obj: RencanaPembelajaranSemester):
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

        # SKS
        sks_form = cleaned_data['sks_form']
        self.mk_semester_obj.mk_kurikulum.teori_sks = sks_form['teori_sks']
        self.mk_semester_obj.mk_kurikulum.praktik_sks = sks_form['praktik_sks']
        self.mk_semester_obj.mk_kurikulum.save()

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
        self.create_dosen_rps_form(PengembangRPS, pengembang_rps_form, 'dosen_pengembang', rps_obj)

        # Dosen Koordinator RPS
        koordinator_rps_form = cleaned_data['koordinator_rps_form']
        self.create_dosen_rps_form(KoordinatorRPS, koordinator_rps_form, 'dosen_koordinator', rps_obj)

        # Dosen Pengampu RPS
        dosen_pengampu_rps_form = cleaned_data['dosen_pengampu_rps_form']
        self.create_dosen_rps_form(DosenPengampuRPS, dosen_pengampu_rps_form, 'dosen_pengampu', rps_obj)

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


class RPSUpdateView(RPSFormView):
    template_name = 'rps/update-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.rps_obj: RencanaPembelajaranSemester = self.mk_semester_obj.rencanapembelajaransemester

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        kwargs['rps_form'].update({
            'instance': self.rps_obj
        })

        return kwargs

    def get_initial(self):
        initial = super().get_initial()

        # SKS
        initial['sks_form'].update({
            'teori_sks': self.mk_semester_obj.mk_kurikulum.teori_sks,
            'praktik_sks': self.mk_semester_obj.mk_kurikulum.praktik_sks,
        })
        
        # Kaprodi
        initial['kaprodi_rps_form'].update({
            'kaprodi': self.rps_obj.kaprodi
        })

        # Pengembang RPS
        list_dosen_pengembang_rps: QuerySet[PengembangRPS] = self.rps_obj.get_pengembang_rps()

        initial['pengembang_rps_form'].update({
            'dosen_pengembang': [dosen.dosen for dosen in list_dosen_pengembang_rps]
        })

        # Koordinator RPS
        list_dosen_koordinator_rps: QuerySet[KoordinatorRPS] = self.rps_obj.get_koordinator_rps()

        initial['koordinator_rps_form'].update({
            'dosen_koordinator': [dosen.dosen for dosen in list_dosen_koordinator_rps]
        })

        # Dosen Pengampu RPS
        list_dosen_pengampu_rps: QuerySet[DosenPengampuRPS] = self.rps_obj.get_dosen_pengampu_rps()

        initial['dosen_pengampu_rps_form'].update({
            'dosen_pengampu': [dosen.dosen for dosen in list_dosen_pengampu_rps]
        })

        # MK Syarat RPS
        list_mata_kuliah_syarat_rps: QuerySet[MataKuliahSyaratRPS] = self.rps_obj.get_mata_kuliah_syarat_rps()

        initial['mata_kuliah_syarat_rps_form'].update({
            'mk_semester_syarat': [mk_syarat.mk_semester for mk_syarat in list_mata_kuliah_syarat_rps]
        })
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        mk_semester_syarat_initial = self.get_forms()['mata_kuliah_syarat_rps_form'].fields['mk_semester_syarat'].initial
        mk_semester_syarat = json.dumps({'results': mk_semester_syarat_initial})

        context.update({
            'mk_semester_syarat': mk_semester_syarat,
        })
        return context
    
    def update_dosen_rps_form(self, model, form_cleaned_data, field_key: str, rps_obj: RencanaPembelajaranSemester, queryset: QuerySet):
        list_dosen_profile = self.get_dosen_profile(form_cleaned_data[field_key])
        list_dosen_user = []

        for dosen_profile in list_dosen_profile:
            dosen_user = authenticate(self.request, user=dosen_profile, role=RoleChoices.DOSEN)
            list_dosen_user.append(dosen_user)
            
            queryset_with_dosen = queryset.filter(
                dosen=dosen_user
            )

            # If query exists, don't need to update
            if queryset_with_dosen.exists(): continue

            # If query doesn't exist, create a new one
            model.objects.create(
                rps=rps_obj,
                dosen=dosen_user
            )
        
        # Search dosen that doesn't appear on list user but in database
        queryset_with_dosen = queryset.exclude(
            dosen__in=list_dosen_user
        )
        # Delete if not on clean_field
        queryset_with_dosen.delete()

    def forms_valid(self, forms: dict):
        cleaned_data = {}

        for key, form in forms.items():
            cleaned_data[key] = form.cleaned_data
        
        # SKS
        sks_form = cleaned_data['sks_form']
        self.mk_semester_obj.mk_kurikulum.teori_sks = sks_form['teori_sks']
        self.mk_semester_obj.mk_kurikulum.praktik_sks = sks_form['praktik_sks']
        self.mk_semester_obj.mk_kurikulum.save()

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
        rps_obj = RencanaPembelajaranSemester.objects.filter(
            id=self.rps_obj.pk,
            mk_semester=self.mk_semester_obj,
        )

        rps_obj.update(
            kaprodi=kaprodi_user,
            **rps_form
        )

        # Dosen pengembang RPS
        pengembang_rps_form = cleaned_data['pengembang_rps_form']
        pengembang_rps_qs: QuerySet[PengembangRPS] = self.rps_obj.get_pengembang_rps()
        self.update_dosen_rps_form(PengembangRPS, pengembang_rps_form, 'dosen_pengembang', self.rps_obj, pengembang_rps_qs)

        # Dosen koordinator RPS
        koordinator_rps_form = cleaned_data['koordinator_rps_form']
        koordinator_rps_qs: QuerySet[KoordinatorRPS] = self.rps_obj.get_koordinator_rps()
        self.update_dosen_rps_form(KoordinatorRPS, koordinator_rps_form, 'dosen_koordinator', self.rps_obj, koordinator_rps_qs)

        # Dosen pengampu RPS
        dosen_pengampu_rps_form = cleaned_data['dosen_pengampu_rps_form']
        dosen_pengampu_rps_qs: QuerySet[DosenPengampuRPS] = self.rps_obj.get_dosen_pengampu_rps()
        self.update_dosen_rps_form(DosenPengampuRPS, dosen_pengampu_rps_form, 'dosen_pengampu', self.rps_obj, dosen_pengampu_rps_qs)

        # Mata Kuliah Syarat
        mata_kuliah_syarat_rps_form = cleaned_data['mata_kuliah_syarat_rps_form']
        mata_kuliah_syarat_rps_qs: QuerySet[MataKuliahSyaratRPS] = self.rps_obj.get_mata_kuliah_syarat_rps()
        list_mk_semester_syarat = []

        for mk_semester_id in mata_kuliah_syarat_rps_form['mk_semester_syarat']:
            try:
                mk_semester_obj = MataKuliahSemester.objects.get(id=mk_semester_id)
            except (MataKuliahSemester.DoesNotExist, MataKuliahSemester.MultipleObjectsReturned):
                message = 'Tidak bisa mendapatkan mata kuliah semester dengan ID: {}'.format(mk_semester_id)
                if settings.DEBUG: print(message)
                messages.error(self.request, message)

                continue

            list_mk_semester_syarat.append(mk_semester_obj)

            queryset_with_mk = mata_kuliah_syarat_rps_qs.filter(
                mk_semester=mk_semester_obj
            )

            # If query exists, don't need to update
            if queryset_with_mk.exists(): continue

            # If query doesn't exist, create a new one
            MataKuliahSyaratRPS.objects.create(
                rps=self.rps_obj,
                mk_semester=mk_semester_obj,
            )

        # Search dosen that doesn't appear on list user but in database
        queryset_with_mk = mata_kuliah_syarat_rps_qs.exclude(
            mk_semester__in=list_mk_semester_syarat
        )
        # Delete if not on clean_field
        queryset_with_mk.delete()

        return super().forms_valid(forms)


class RPSDeleteView(DeleteView):
    model = RencanaPembelajaranSemester

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.success_url = self.mk_semester_obj.get_rps_home_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return self.delete(request, *args, **kwargs)
    
    def get_object(self, queryset = None):
        obj = self.mk_semester_obj.rencanapembelajaransemester
        return obj


class RPSLockAndUnlockView(RedirectView):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

    def get_redirect_url(self, *args, **kwargs):
        self.url = self.mk_semester_obj.get_rps_home_url()
        return super().get_redirect_url(*args, **kwargs)
    
    def lock_child(self, is_locking_success: bool, is_success: bool, obj):
        is_locking_success = is_locking_success and obj.lock_object(self.request.user)
        is_success = is_success and obj.is_locked

        print('L {}, S {}, {}'.format(is_locking_success, is_success, obj))

        return is_locking_success, is_success
        
    def lock_children(self, is_locking_success: bool, is_success: bool, queryset: QuerySet):
        for obj in queryset:
            is_locking_success, is_success = self.lock_child(is_locking_success, is_success, obj)
        
        return is_locking_success, is_success
    
    def unlock_child(self, is_unlocking_success: bool, is_success: bool, obj):
        is_unlocking_success = is_unlocking_success and obj.unlock_object()
        is_success = is_success and not obj.is_locked

        return is_unlocking_success, is_success
        
    def unlock_children(self, is_unlocking_success: bool, is_success: bool, queryset: QuerySet):
        for obj in queryset:
            is_unlocking_success, is_success = self.unlock_child(is_unlocking_success, is_success, obj)
        
        return is_unlocking_success, is_success
    
    def lock_rps(self):
        is_success = True
        is_locking_success = True

        # RPS
        rps_obj: RencanaPembelajaranSemester = self.mk_semester_obj.rencanapembelajaransemester
        
        # Dosen Pengembang RPS
        pengembang_rps_qs: QuerySet[PengembangRPS] = rps_obj.get_pengembang_rps()
        is_locking_success, is_success = self.lock_children(is_locking_success, is_success, pengembang_rps_qs)

        # Koordinator RPS
        koordinator_rps_qs: QuerySet[KoordinatorRPS] = rps_obj.get_koordinator_rps()
        is_locking_success, is_success = self.lock_children(is_locking_success, is_success, koordinator_rps_qs)

        # Dosen Pengampu RPS
        dosen_pengampu_rps: QuerySet[DosenPengampuRPS] = rps_obj.get_dosen_pengampu_rps()
        is_locking_success, is_success = self.lock_children(is_locking_success, is_success, dosen_pengampu_rps)

        # MK Syarat RPS
        mk_syarat_rps: QuerySet[MataKuliahSyaratRPS] = rps_obj.get_mata_kuliah_syarat_rps()
        is_locking_success, is_success = self.lock_children(is_locking_success, is_success, mk_syarat_rps)

        # Lock RPS
        is_locking_success, is_success = self.lock_child(is_locking_success, is_success, rps_obj)

        # Pertemuan
        pertemuan_qs: QuerySet[PertemuanRPS] = self.mk_semester_obj.get_all_pertemuan_rps()

        for pertemuan in pertemuan_qs:
            if hasattr(pertemuan, 'rincianpertemuanrps'):
                # Rincian Pertemuan
                rincian_pertemuan_obj: RincianPertemuanRPS = pertemuan.rincianpertemuanrps
                is_locking_success, is_success = self.lock_child(is_locking_success, is_success, rincian_pertemuan_obj)

            # Pembelajaran Pertemuan
            pembelajaran_pertemuan_rps_qs: QuerySet[PembelajaranPertemuanRPS] = pertemuan.get_all_pembelajaran_pertemuan()
            is_locking_success, is_success = self.lock_children(is_locking_success, is_success, pembelajaran_pertemuan_rps_qs)

            # Durasi Pertemuan
            durasi_pertemuan_rps_qs: QuerySet[DurasiPertemuanRPS] = pertemuan.get_all_durasi_pertemuan()
            is_locking_success, is_success = self.lock_children(is_locking_success, is_success, durasi_pertemuan_rps_qs)

            # Lock pertemuan
            is_locking_success, is_success = self.lock_child(is_locking_success, is_success, pertemuan)
        
        if is_success:
            self.mk_semester_obj.is_rps_locked = True
            self.mk_semester_obj.save()

        return is_success, is_locking_success
    
    def unlock_rps(self):
        is_success = True
        is_unlocking_success = True

        # RPS
        rps_obj: RencanaPembelajaranSemester = self.mk_semester_obj.rencanapembelajaransemester
        
        # Dosen Pengembang RPS
        pengembang_rps_qs: QuerySet[PengembangRPS] = rps_obj.get_pengembang_rps()
        is_unlocking_success, is_success = self.unlock_children(is_unlocking_success, is_success, pengembang_rps_qs)

        # Koordinator RPS
        koordinator_rps_qs: QuerySet[KoordinatorRPS] = rps_obj.get_koordinator_rps()
        is_unlocking_success, is_success = self.unlock_children(is_unlocking_success, is_success, koordinator_rps_qs)

        # Dosen Pengampu RPS
        dosen_pengampu_rps: QuerySet[DosenPengampuRPS] = rps_obj.get_dosen_pengampu_rps()
        is_unlocking_success, is_success = self.unlock_children(is_unlocking_success, is_success, dosen_pengampu_rps)

        # MK Syarat RPS
        mk_syarat_rps: QuerySet[MataKuliahSyaratRPS] = rps_obj.get_mata_kuliah_syarat_rps()
        is_unlocking_success, is_success = self.unlock_children(is_unlocking_success, is_success, mk_syarat_rps)

        # Lock RPS
        is_unlocking_success, is_success = self.unlock_child(is_unlocking_success, is_success, rps_obj)

        # Pertemuan
        pertemuan_qs: QuerySet[PertemuanRPS] = self.mk_semester_obj.get_all_pertemuan_rps()

        for pertemuan in pertemuan_qs:
            if hasattr(pertemuan, 'rincianpertemuanrps'):
                # Rincian Pertemuan
                rincian_pertemuan_obj: RincianPertemuanRPS = pertemuan.rincianpertemuanrps
                is_unlocking_success, is_success = self.unlock_child(is_unlocking_success, is_success, rincian_pertemuan_obj)

            # Pembelajaran Pertemuan
            pembelajaran_pertemuan_rps_qs: QuerySet[PembelajaranPertemuanRPS] = pertemuan.get_all_pembelajaran_pertemuan()
            is_unlocking_success, is_success = self.unlock_children(is_unlocking_success, is_success, pembelajaran_pertemuan_rps_qs)

            # Durasi Pertemuan
            durasi_pertemuan_rps_qs: QuerySet[DurasiPertemuanRPS] = pertemuan.get_all_durasi_pertemuan()
            is_unlocking_success, is_success = self.unlock_children(is_unlocking_success, is_success, durasi_pertemuan_rps_qs)

            # Lock pertemuan
            is_unlocking_success, is_success = self.unlock_child(is_unlocking_success, is_success, pertemuan)
        
        if is_success:
            self.mk_semester_obj.is_rps_locked = False
            self.mk_semester_obj.save()

        return is_success, is_unlocking_success


class RPSLockView(RPSLockAndUnlockView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        total_bobot_penilaian = self.mk_semester_obj.get_total_bobot_penilaian_pertemuan_rps

        # Can't lock if total persentase CLO is not 100%
        if total_bobot_penilaian != 100: 
            messages.warning(request, 'Gagal mengunci RPS dan pertemuannya. Pastikan total bobot penilaian adalah 100%.')
            return super().get(request, *args, **kwargs)

        is_locking_success, is_success = self.lock_rps()

        if not is_locking_success:
            messages.info(request, 'RPS dan pertemuannya sudah terkunci.')
            return super().get(request, *args, **kwargs)
            
        if is_success:
            messages.success(request, 'Berhasil mengunci RPS dan pertemuannya.')
        else:
            # Undo
            self.unlock_rps()
            messages.error(request, 'Gagal mengunci RPS dan pertemuannya.')
        return super().get(request, *args, **kwargs)


class RPSUnlockView(RPSLockAndUnlockView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        is_unlocking_success, is_success = self.unlock_rps()

        if not is_unlocking_success:
            messages.info(request, 'RPS dan pertemuannya tidak terkunci.')
            return super().get(request, *args, **kwargs)
            
        if is_success:
            messages.success(request, 'Berhasil membuka kunci RPS dan pertemuannya.')
        else:
            # Undo
            self.lock_rps()
            messages.error(request, 'Gagal membuka kunci RPS dan pertemuannya.')
        return super().get(request, *args, **kwargs)


# Pertemuan RPS
class PertemuanRPSCreateView(CreateView):
    template_name = 'rps/pertemuan/create-view.html'
    model = PertemuanRPS
    form_class = PertemuanRPSForm

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.success_url = '{}?active_tab=pertemuan'.format(self.mk_semester_obj.get_rps_home_url())
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        total_bobot_penilaian = self.mk_semester_obj.get_total_bobot_penilaian_pertemuan_rps

        # If total_persentase is 100, no need to add anymore
        if total_bobot_penilaian >= 100:
            messages.info(self.request, 'Sudah tidak bisa menambahkan pertemuan lagi, karena total bobot penilaian sudah {}%'.format(total_bobot_penilaian))
            return redirect(self.success_url)
        
        return super().get(request, *args, **kwargs)

    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'clo_qs': self.mk_semester_obj.get_all_clo(),
            'pertemuan_rps_qs': self.mk_semester_obj.get_all_pertemuan_rps()
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
        })
        return context
    
    def form_valid(self, form) -> HttpResponse:
        pertemuan_rps_obj: PertemuanRPS = form.save(commit=False)
        pertemuan_rps_obj.mk_semester = self.mk_semester_obj
        pertemuan_rps_obj.save()

        return redirect(self.success_url)


class PertemuanRPSBulkDeleteView(ModelBulkDeleteView):
    model = PertemuanRPS
    id_list_obj: str = 'id_pertemuan_rps'
    success_msg: str = 'Berhasil menghapus pertemuan RPS.'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj: MataKuliahSemester = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.success_url = '{}?active_tab=pertemuan'.format(self.mk_semester_obj.get_rps_home_url())
        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id__in=self.get_list_selected_obj())
        return super().get_queryset()


class PertemuanRPSReadView(DetailView):
    model = PertemuanRPS
    pk_url_kwarg = 'pertemuan_rps_id'
    template_name = 'rps/pertemuan/detail-view.html'


class PertemuanRPSUpdateView(UpdateView):
    template_name = 'rps/pertemuan/update-view.html'
    model = PertemuanRPS
    pk_url_kwarg = 'pertemuan_rps_id'
    form_class = PertemuanRPSForm

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.object: PertemuanRPS = self.get_object()
        self.success_url = self.object.read_detail_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'clo_qs': self.object.mk_semester.get_all_clo(),
            'pertemuan_rps_qs': self.object.mk_semester.get_all_pertemuan_rps(),
            'current_pertemuan_rps': self.object,
        })
        return kwargs


class RincianPertemuanRPSFormView(MultiModelFormView):
    form_classes = {
        'rincian_pertemuan_rps_form': RincianPertemuanRPSForm,
        'pembelajaran_pertemuan_luring_rps_form': PembelajaranPertemuanLuringRPSForm,
        'pembelajaran_pertemuan_daring_rps_form': PembelajaranPertemuanDaringRPSForm,
        'durasi_pertemuan_luring_rps_formset': DurasiPertemuanLuringRPSFormset,
        'durasi_pertemuan_daring_rps_formset': DurasiPertemuanDaringRPSFormset,
    }
    success_msg = 'Berhasil'
    failed_msg = 'Gagal'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        pertemuan_rps_id = kwargs.get('pertemuan_rps_id')
        self.pertemuan_rps_obj = get_object_or_404(PertemuanRPS, id=pertemuan_rps_id)
        self.success_url = self.pertemuan_rps_obj.read_detail_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['durasi_pertemuan_luring_rps_formset'].update({
            'prefix': 'durasi_pertemuan_luring',
            'queryset': self.pertemuan_rps_obj.get_durasi_pertemuan_luring(),
        })

        kwargs['durasi_pertemuan_daring_rps_formset'].update({
            'prefix': 'durasi_pertemuan_daring',
            'queryset': self.pertemuan_rps_obj.get_durasi_pertemuan_daring(),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'pertemuan_rps_obj': self.pertemuan_rps_obj,
        })
        return context
    
    def get_objects(self):
        objects = super().get_objects()
        objects['durasi_pertemuan_luring_rps_formset'] = self.pertemuan_rps_obj
        objects['durasi_pertemuan_daring_rps_formset'] = self.pertemuan_rps_obj
        
        return objects
    
    def forms_valid(self, forms: dict):
        messages.success(self.request, self.success_msg)
        return super().forms_valid(forms)
    
    def forms_invalid(self, forms: dict):
        messages.error(self.request, self.failed_msg)
        return super().forms_invalid(forms)


class RincianPertemuanRPSCreateView(RincianPertemuanRPSFormView):
    template_name = 'rps/pertemuan/rincian-pertemuan-create-view.html'
    success_msg = 'Berhasil menambahkan rincian pertemuan RPS.'
    failed_msg = 'Gagal menambahkan rincian pertemuan RPS.'

    def get(self, request, *args, **kwargs):
        if hasattr(self.pertemuan_rps_obj, 'rincianpertemuanrps'):
            messages.info(request, 'Rincian pertemuan RPS sudah ada.')
            return redirect(self.success_url)
        
        return super().get(request, *args, **kwargs)

    def forms_valid(self, forms: dict):
        # Rincian RPS
        rincian_pertemuan_rps_obj: RincianPertemuanRPS = forms['rincian_pertemuan_rps_form'].save(commit=False)
        rincian_pertemuan_rps_obj.pertemuan_rps = self.pertemuan_rps_obj
        rincian_pertemuan_rps_obj.save()
        
        # Pembelajaran Pertemuan Luring RPS
        pembelajaran_pertemuan_luring_rps_obj: PembelajaranPertemuanRPS = forms['pembelajaran_pertemuan_luring_rps_form'].save(commit=False)
        pembelajaran_pertemuan_luring_rps_obj.pertemuan_rps = self.pertemuan_rps_obj
        pembelajaran_pertemuan_luring_rps_obj.save()
        
        # Pembelajaran Pertemuan Daring RPS
        pembelajaran_pertemuan_daring_rps_obj: PembelajaranPertemuanRPS = forms['pembelajaran_pertemuan_daring_rps_form'].save(commit=False)
        pembelajaran_pertemuan_daring_rps_obj.pertemuan_rps = self.pertemuan_rps_obj
        pembelajaran_pertemuan_daring_rps_obj.save()

        return super().forms_valid(forms)


class RincianPertemuanRPSUpdateView(RincianPertemuanRPSFormView):
    template_name = 'rps/pertemuan/rincian-pertemuan-update-view.html'
    success_msg = 'Berhasil mengubah rincian pertemuan RPS.'
    failed_msg = 'Gagal mengubah rincian pertemuan RPS.'
    
    def get_objects(self):
        objects = super().get_objects()
        objects['rincian_pertemuan_rps_form'] = self.pertemuan_rps_obj.rincianpertemuanrps

        objects['pembelajaran_pertemuan_luring_rps_form'] = self.pertemuan_rps_obj.get_pembelajaran_pertemuan_luring().first()

        objects['pembelajaran_pertemuan_daring_rps_form'] = self.pertemuan_rps_obj.get_pembelajaran_pertemuan_daring().first()
        return objects


class RPSDuplicateView(DuplicateFormview):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj: MataKuliahSemester = get_object_or_404(MataKuliahSemester, id=mk_semester_id)

        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi

        self.success_url = self.mk_semester_obj.get_rps_home_url()
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'mk_semester': self.mk_semester_obj,
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
            'back_url': self.success_url,
        })
        return context


class RincianRPSDuplicateView(RPSDuplicateView):
    form_class = RincianRPSDuplicateForm
    empty_choices_msg = 'Semester lain belum mempunyai RPS.'
    template_name = 'rps/duplicate-view.html'
    
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        
        self.choices = get_semester_choices_rincian_rps_duplicate(self.mk_semester_obj)

    def form_valid(self, form) -> HttpResponse:
        semester_prodi_id = form.cleaned_data.get('semester')

        is_success, message = duplicate_rincian_rps(semester_prodi_id, self.mk_semester_obj)
        self.show_clone_result_message(is_success, message)

        return super().form_valid(form)


class PertemuanRPSDuplicateView(RPSDuplicateView):
    form_class = PertemuanRPSDuplicateForm
    empty_choices_msg = 'Semester lain belum mempunyai pertemuan di RPS.'
    template_name = 'rps/pertemuan/duplicate-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        
        self.success_url = '{}?active_tab=pertemuan'.format(self.success_url)
        self.choices = get_semester_choices_pertemuan_rps_duplicate(self.mk_semester_obj)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        total_bobot_penilaian = self.mk_semester_obj.get_total_bobot_penilaian_pertemuan_rps

        # If total_persentase is 100, no need to add anymore
        if total_bobot_penilaian >= 100:
            messages.info(self.request, 'Sudah tidak bisa menambahkan pertemuan lagi, karena total bobot penilaian sudah {}%'.format(total_bobot_penilaian))
            return redirect(self.success_url)
        
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form) -> HttpResponse:
        semester_prodi_id = form.cleaned_data.get('semester')

        is_success, message = duplicate_pertemuan_rps(semester_prodi_id, self.mk_semester_obj)
        self.show_clone_result_message(is_success, message)
        
        # If current duplicated percentages is more than 100, add warning message
        current_total_bobot_penilaian = self.mk_semester_obj.get_total_bobot_penilaian_pertemuan_rps
        if current_total_bobot_penilaian > 100:
            messages.warning(self.request, 'Total persentase saat ini: {}. Diharap untuk mengubah pertemuan RPS agar mencukupi 100%'.format(current_total_bobot_penilaian))
        
        return super().form_valid(form)
