import os
from django.conf import settings
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import CreateView, UpdateView
from mata_kuliah_semester.models import MataKuliahSemester
from learning_outcomes_assessment.auth.mixins import(
    ProgramStudiMixin,
    MahasiswaAndMKSemesterMixin
)
from .mixins import RPSLockedObjectPermissionMixin
from .models import RencanaPembelajaranSemester
from .forms import RPSModelForm


# Create your views here.
class RPSHomeView(ProgramStudiMixin, MahasiswaAndMKSemesterMixin, PermissionRequiredMixin, TemplateView):
    permission_required = ('rps.view_rencanapembelajaransemester',)
    template_name = 'rps/home.html'
    rps_obj: RencanaPembelajaranSemester = None
    rps_filename = 'RPS-'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
        if hasattr(self.mk_semester_obj, 'rencanapembelajaransemester'):
            self.rps_obj = self.mk_semester_obj.rencanapembelajaransemester
            self.rps_filename = 'RPS-{}-{}.pdf'.format(self.mk_semester_obj.mk_kurikulum.nama, self.mk_semester_obj.semester.semester.nama)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if 'download_rps' in request.GET:
            if not request.is_ajax(): raise PermissionDenied
            return self.download_rps()
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
            'rps_filename': self.rps_filename,
        })
        return context
    
    def download_rps(self) -> HttpResponse:
        if self.rps_obj is None:
            return HttpResponse('Gagal')
        
        as_attachment = True
        response = FileResponse(self.rps_obj.file_rps, as_attachment=as_attachment, filename=self.rps_filename)

        return response


class RPSCreateView(ProgramStudiMixin, RPSLockedObjectPermissionMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('rps.add_rencanapembelajaransemester',)
    form_class = RPSModelForm
    model = RencanaPembelajaranSemester
    template_name = 'rps/create-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
        self.success_url = self.mk_semester_obj.get_rps_home_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
        })
        return context
    
    def form_valid(self, form):
        form.instance.mk_semester = self.mk_semester_obj
        self.object: RencanaPembelajaranSemester = form.save()

        # Change permission
        os.chmod(self.object.file_rps.path, 0o600)
        messages.success(self.request, 'Berhasil menambah RPS.')
        return redirect(self.success_url)
    

class RPSUpdateView(ProgramStudiMixin, RPSLockedObjectPermissionMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('rps.change_rencanapembelajaransemester',)
    model = RencanaPembelajaranSemester
    form_class = RPSModelForm
    template_name = 'rps/update-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
        self.success_url = self.mk_semester_obj.get_rps_home_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not hasattr(self.mk_semester_obj, 'rencanapembelajaransemester'):
            messages.info(request, 'Mata kuliah belum mempunyai RPS.')
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None) -> RencanaPembelajaranSemester:
        print('get obj')
        if hasattr(self.mk_semester_obj, 'rencanapembelajaransemester'):
            return self.mk_semester_obj.rencanapembelajaransemester
        
        return super().get_object(queryset)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mk_semester_obj': self.mk_semester_obj,
        })
        return context
    
    def post(self, request: HttpRequest, *args: str, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        old_file_path = self.object.file_rps.path

        form = self.get_form()
        if form.is_valid():
            if form.has_changed():
                # Remove previous file
                os.remove(old_file_path)
                return self.form_valid(form)
            else:
                return redirect(self.success_url)
        else:
            return self.form_invalid(form)
        
    def form_valid(self, form):
        self.object: RencanaPembelajaranSemester = form.save()

        # Change permission
        os.chmod(self.object.file_rps.path, 0o600)
        messages.success(self.request, 'Berhasil meng-update RPS.')
        return redirect(self.success_url)
    

class RPSDeleteView(ProgramStudiMixin, RPSLockedObjectPermissionMixin, PermissionRequiredMixin, RedirectView):
    permission_required = ('rps.delete_rencanapembelajaransemester',)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
        self.url = self.mk_semester_obj.get_rps_home_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not hasattr(self.mk_semester_obj, 'rencanapembelajaransemester'):
            messages.info(request, 'Mata kuliah belum mempunyai RPS.')
        else:
            self.rps_obj: RencanaPembelajaranSemester = self.mk_semester_obj.rencanapembelajaransemester
            old_file_path = self.rps_obj.file_rps.path
            self.rps_obj.delete()

            try:
                # Remove file
                os.remove(old_file_path)
            except FileNotFoundError:
                if settings.DEBUG:
                    print('File not found. Path: {}'.format(self.rps_obj.file_rps.path))

            messages.success(request, 'Berhasil menghapus RPS.')
        return super().get(request, *args, **kwargs)


class RPSLockAndUnlockTemplateView(ProgramStudiMixin, RedirectView):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.program_studi_obj = self.mk_semester_obj.mk_kurikulum.kurikulum.prodi_jenjang.program_studi
    
    def get_redirect_url(self, *args, **kwargs):
        self.url = self.mk_semester_obj.get_rps_home_url()
        return super().get_redirect_url(*args, **kwargs)
    
    def lock_rps(self):
        is_success = True
        is_locking_success = True

        # RPS
        rps_obj: RencanaPembelajaranSemester = self.mk_semester_obj.rencanapembelajaransemester

        is_locking_success = is_locking_success and rps_obj.lock_object(self.request.user)
        is_success = is_success and rps_obj.is_locked

        if is_success:
            self.mk_semester_obj.is_rencanapembelajaransemester_locked = True
            self.mk_semester_obj.save()

        return is_locking_success, is_success


    def unlock_rps(self):
        is_success = True
        is_unlocking_success = True

        # RPS
        rps_obj: RencanaPembelajaranSemester = self.mk_semester_obj.rencanapembelajaransemester

        is_unlocking_success = is_unlocking_success and rps_obj.unlock_object()
        is_success = is_success and not rps_obj.is_locked

        if is_success:
            self.mk_semester_obj.is_rencanapembelajaransemester_locked = False
            self.mk_semester_obj.save()

        return is_unlocking_success, is_success


class RPSLockView(PermissionRequiredMixin, RPSLockAndUnlockTemplateView):
    permission_required = (
        'rps.change_rencanapembelajaransemester',
        'mata_kuliah_semester.change_matakuliahsemester',
        'lock_model.add_lock',
        'lock_model.change_lock',
    )

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not hasattr(self.mk_semester_obj, 'rencanapembelajaransemester'):
            messages.info(request, 'Mata kuliah belum mempunyai RPS.')
            return super().get(request, *args, **kwargs)
        
        is_locking_success, is_success = self.lock_rps()

        if not is_locking_success:
            messages.info(request, 'RPS sudah terkunci.')
            return super().get(request, *args, **kwargs)
            
        if is_success:
            messages.success(request, 'Berhasil mengunci RPS.')
        else:
            # Undo
            self.unlock_rps()
            messages.error(request, 'Gagal mengunci RPS.')
        return super().get(request, *args, **kwargs)


class RPSUnlockView(PermissionRequiredMixin, RPSLockAndUnlockTemplateView):
    permission_required = (
        'mata_kuliah_semester.change_matakuliahsemester',
        'lock_model.change_lock',
    )

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not hasattr(self.mk_semester_obj, 'rencanapembelajaransemester'):
            messages.info(request, 'Mata kuliah belum mempunyai RPS.')
            return super().get(request, *args, **kwargs)
        
        is_unlocking_success, is_success = self.unlock_rps()

        if not is_unlocking_success:
            messages.info(request, 'RPS tidak terkunci.')
            return super().get(request, *args, **kwargs)
            
        if is_success:
            messages.success(request, 'Berhasil membuka kunci RPS.')
        else:
            # Undo
            self.lock_rps()
            messages.error(request, 'Gagal membuka kunci RPS.')
        return super().get(request, *args, **kwargs)
