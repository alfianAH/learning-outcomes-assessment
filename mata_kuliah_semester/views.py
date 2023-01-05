from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from learning_outcomes_assessment.forms.edit import ModelBulkDeleteView
from learning_outcomes_assessment.list_view.views import ListViewModelA
from semester.models import SemesterProdi
from .forms import (
    MataKuliahSemesterCreateForm,
)
from mata_kuliah_kurikulum.models import(
    MataKuliahKurikulum
)
from .models import (
    MataKuliahSemester,
)
from .utils import(
    get_mk_semester_choices
)


# Create your views here.
class MataKuliahSemesterCreateView(FormView):
    form_class = MataKuliahSemesterCreateForm
    template_name: str = 'mata-kuliah-semester/create-view.html'
    semester_obj: SemesterProdi = None
    mk_semester_choices = []

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        semester_prodi_id = kwargs.get('semester_prodi_id')
        self.semester_obj: SemesterProdi = get_object_or_404(SemesterProdi, id_neosia=semester_prodi_id)

        self.mk_semester_choices = get_mk_semester_choices(self.semester_obj.id_neosia)

        self.success_url = self.semester_obj.read_detail_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if len(self.mk_semester_choices) == 0:
            messages.info(request, 'Pilihan mata kuliah semester kosong. Ada kemungkinan data sudah disinkronisasi atau mata kuliah pada kurikulum belum ditambahkan.')
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'semester_obj': self.semester_obj,
            'back_url': self.success_url,
            'submit_text': 'Tambahkan'
        })
        return context

    def get_form(self, form_class = None):
        form = super().get_form(form_class)
        form.fields['mk_from_neosia'].choices = self.mk_semester_choices
        return form

    def form_valid(self, form) -> HttpResponse:
        list_mk_kurikulum_id = form.cleaned_data.get('mk_from_neosia')

        for mk_kurikulum_id in list_mk_kurikulum_id:
            # Convert mk kurikulum to integer
            try:
                mk_kurikulum_id = int(mk_kurikulum_id)
            except ValueError:
                if settings.DEBUG:
                    print('Cannot convert MK Kurikulum ID: "{}" to integer'.format(mk_kurikulum_id))
                messages.error(self.request, 'Tidak bisa mengonversi MK Kurikulum ID: {} ke integer'.format(mk_kurikulum_id))
                continue
            
            # Get MK Kurikulum object
            try:
                mk_kurikulum_obj = MataKuliahKurikulum.objects.get(id_neosia=mk_kurikulum_id)
            except MataKuliahKurikulum.DoesNotExist:
                if settings.DEBUG:
                    print('MK Kurikulum object not found. ID: {}'.format(mk_kurikulum_id))
                messages.error(self.request, 'Tidak dapat menemukan mata kuliah kurikulum dengan ID: {}'.format(mk_kurikulum_id))
                continue
            except MataKuliahKurikulum.MultipleObjectsReturned:
                if settings.DEBUG:
                    print('MK Kurikulum with ID({}) returns multiple objects.'.format(mk_kurikulum_id))
                continue
            
            # Create MK Semester
            MataKuliahSemester.objects.create(
                mk_kurikulum=mk_kurikulum_obj,
                semester=self.semester_obj
            )
        
        messages.success(self.request, 'Proses menambahkan mata kuliah semester sudah selesai')

        return super().form_valid(form)


class MataKuliahSemesterUpdateView(FormView):
    pass


class MataKuliahSemesterReadView(DetailView):
    pass


class MataKuliahSemesterBulkDeleteView(ModelBulkDeleteView):
    model = MataKuliahSemester
    id_list_obj = 'id_mk_semester'
    success_msg = 'Berhasil mmenghapus mata kuliah semester'

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        semester_prodi_id = kwargs.get('semester_prodi_id')
        semester_prodi_obj = get_object_or_404(SemesterProdi, id_neosia=semester_prodi_id)
        self.success_url = semester_prodi_obj.read_detail_url()

    def get_queryset(self):
        self.queryset = self.model.objects.filter(id__in=self.get_list_selected_obj())
        return super().get_queryset()
