import os
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import CreateView, UpdateView
from mata_kuliah_semester.models import MataKuliahSemester
from .models import RencanaPembelajaranSemester
from .forms import RPSModelForm


# Create your views here.
class RPSHomeView(TemplateView):
    template_name = 'rps/home.html'
    rps_obj: RencanaPembelajaranSemester = None
    rps_filename = 'RPS-'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
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


class RPSCreateView(CreateView):
    form_class = RPSModelForm
    model = RencanaPembelajaranSemester
    template_name = 'rps/create-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
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
    

class RPSUpdateView(UpdateView):
    model = RencanaPembelajaranSemester
    form_class = RPSModelForm
    template_name = 'rps/update-view.html'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
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
            # Remove previous file
            os.remove(old_file_path)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
    def form_valid(self, form):
        self.object: RencanaPembelajaranSemester = form.save()

        # Change permission
        os.chmod(self.object.file_rps.path, 0o600)
        messages.success(self.request, 'Berhasil meng-update RPS.')
        return redirect(self.success_url)
    

class RPSDeleteView(RedirectView):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        mk_semester_id = kwargs.get('mk_semester_id')
        self.mk_semester_obj = get_object_or_404(MataKuliahSemester, id=mk_semester_id)
        self.url = self.mk_semester_obj.get_rps_home_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not hasattr(self.mk_semester_obj, 'rencanapembelajaransemester'):
            messages.info(request, 'Mata kuliah belum mempunyai RPS.')
        else:
            self.rps_obj: RencanaPembelajaranSemester = self.mk_semester_obj.rencanapembelajaransemester
            # Remove file
            os.remove(self.rps_obj.file_rps.path)
            self.rps_obj.delete()
        return super().get(request, *args, **kwargs)


class RPSLockAndUnlockTemplateView(RedirectView):
    pass


class RPSLockView(RPSLockAndUnlockTemplateView):
    pass


class RPSUnlockView(RPSLockAndUnlockTemplateView):
    pass



