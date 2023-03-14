from django.forms import BaseFormSet
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from semester.models import (
    TahunAjaranProdi,
    SemesterProdi,
)
from .forms import (
    KurikulumChoiceForm,
    TahunAjaranSemesterFormset,
)


# Create your views here.
class GetTahunAjaranJsonResponse(TemplateView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        selected_kurikulum_id = request.GET.get('kurikulum_id', '')
        tahun_ajaran_choices = [('', '---------')]

        # If kurikulum_id is empty str or request is not AJAX, return
        if not selected_kurikulum_id.strip() or not request.is_ajax(): 
            return JsonResponse({'choices': tahun_ajaran_choices})
        
        tahun_ajaran_prodi_qs = TahunAjaranProdi.objects.filter(
            semesterprodi__matakuliahsemester__mk_kurikulum__kurikulum__id_neosia=selected_kurikulum_id
        ).distinct()
        tahun_ajaran_choices += [(tahun_ajaran_prodi.pk, str(tahun_ajaran_prodi.tahun_ajaran)) for tahun_ajaran_prodi in tahun_ajaran_prodi_qs]

        return JsonResponse({'choices': tahun_ajaran_choices})
    

class GetSemesterJsonResponse(TemplateView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        selected_tahun_ajaran_id: str = request.GET.get('tahun_ajaran_id', '')
        semester_choices = [('', '---------')]

        # If tahun_ajaran_id is empty str or request is not AJAX, return
        if not selected_tahun_ajaran_id.strip() or not request.is_ajax(): 
            return JsonResponse({'choices': semester_choices})
        
        semester_prodi_qs = SemesterProdi.objects.filter(
            tahun_ajaran_prodi=selected_tahun_ajaran_id
        )
        semester_choices += [(semester_prodi.pk, str(semester_prodi.semester.nama)) for semester_prodi in semester_prodi_qs]

        return JsonResponse({'choices': semester_choices})


class LaporanCapaianPembelajaranView(FormView):
    template_name = 'laporan-cpl/home.html'
    form_class = KurikulumChoiceForm
    formset_class = TahunAjaranSemesterFormset
    success_url = reverse_lazy('laporan_cpl:home')

    def get_formset_class(self):
        return self.formset_class

    def get_formset(self, formset_class=None) -> BaseFormSet:
        if formset_class is None:
            formset_class = self.get_formset_class()

        return formset_class(self.request.POST or None)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'prodi': self.request.user.prodi,
        })
        return kwargs
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form()
        formset = self.get_formset()

        if all([form.is_valid(), formset.is_valid()]):
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'formset' not in context:
            context['formset'] = self.get_formset()
        
        return context

    def form_valid(self, form, formset) -> HttpResponse:
        return self.render_to_response(
            self.get_context_data(
                form=form,
                formset=formset
            )
        )
    
    def form_invalid(self, form, formset) -> HttpResponse:
        return self.render_to_response(
            self.get_context_data(
                form=form,
                formset=formset
            )
        )
