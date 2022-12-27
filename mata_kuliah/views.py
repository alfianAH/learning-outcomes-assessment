from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from learning_outcomes_assessment.list_view.views import ListViewModelA
from semester.models import SemesterKurikulum
from .filters import (
    MataKuliahSemesterFilter,
    MataKuliahSemesterSort,
)
from .forms import (
    MataKuliahSemesterCreateForm,
)
from .models import (
    MataKuliahSemester,
)
from .utils import(
    get_mk_semester_choices
)


# Create your views here.
class MataKuliahSemesterReadAllView(ListViewModelA):
    model = MataKuliahSemester
    paginate_by: int = 10
    template_name: str = 'mata-kuliah/mk-semester-home.html'
    ordering: str = 'mk_kurikulum__nama'
    sort_form_ordering_by_key: str = 'ordering_by'
    semester_obj: SemesterKurikulum = None

    filter_form: MataKuliahSemesterFilter = None
    sort_form: MataKuliahSemesterSort = None

    bulk_delete_url: str = ''
    reset_url: str = ''
    list_prefix_id: str = 'mk-semester-'
    input_name: str = 'id_mk_semester'
    list_id: str = 'mk-semester-list-content'
    list_custom_field_template: str = 'mata-kuliah/partials/list-custom-field-mk-semester.html'
    table_custom_field_header_template: str = 'mata-kuliah/partals/table-custom-field-header-mk-semester.html'
    table_custom_field_template: str = 'mata-kuliah/partials/table-custom-field-mk-semester.html'
    filter_template: str = 'mata-kuliah/partials/mk-semester-filter-form.html'
    sort_template: str = 'mata-kuliah/partials/mk-semester-sort-form.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        semester_kurikulum_id = kwargs.get('semester_kurikulum_id')
        self.semester_obj: SemesterKurikulum = get_object_or_404(SemesterKurikulum, id=semester_kurikulum_id)

        # self.bulk_delete_url = self.semester_obj.get_mk_semester_bulk_delete_url()
        self.reset_url = self.semester_obj.read_all_mk_semester_url()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        mk_semester_qs = self.model.objects.filter(semester=self.semester_obj.pk)

        if mk_semester_qs.exists():
            filter_data = {
                'nama': request.GET.get('nama', ''),
                'sks': request.GET.get('sks', ''),
            }

            sort_data = {
                self.sort_form_ordering_by_key: request.GET.get(self.sort_form_ordering_by_key, self.ordering)
            }

            self.filter_form = MataKuliahSemesterFilter(
                data=filter_data or None,
                queryset=mk_semester_qs
            )
            self.sort_form = MataKuliahSemesterSort(data=sort_data)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            semester=self.semester_obj.pk
        )
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'semester_obj': self.semester_obj,
            'mk_semester_create_url': self.semester_obj.get_create_mk_semester_url(),
            'mk_semester_update_url': self.semester_obj.get_update_mk_semester_url(),
        })
        return context


class MataKuliahSemesterCreateView(FormView):
    form_class = MataKuliahSemesterCreateForm
    template_name: str = 'mata-kuliah/mk-semester-create-view.html'
    semester_obj: SemesterKurikulum = None
    mk_semester_choices = []

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        semester_kurikulum_id = kwargs.get('semester_kurikulum_id')
        self.semester_obj: SemesterKurikulum = get_object_or_404(SemesterKurikulum, id=semester_kurikulum_id)

        prodi_id: int = request.user.prodi.id_neosia
        self.mk_semester_choices = get_mk_semester_choices(prodi_id, self.semester_obj.semester.id_neosia)

        self.success_url = self.semester_obj.read_all_mk_semester_url()

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
        #TODO: NOT YET IMPLEMENTED
        return super().form_valid(form)


class MataKuliahSemesterUpdateView(FormView):
    pass


class MataKuliahSemesterReadView(DetailView):
    pass
