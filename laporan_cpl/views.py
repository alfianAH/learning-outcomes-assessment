import json
from django.db.models import QuerySet
from django.contrib import messages
from django.forms import BaseFormSet
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from semester.models import (
    TahunAjaranProdi,
    SemesterProdi,
)
from ilo.models import Ilo
from .forms import (
    KurikulumChoiceForm,
    TahunAjaranSemesterFormset,
)
from .utils import (
    get_ilo_and_sks_from_kurikulum,
    process_filter_laporan_cpl
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

    def get_formset_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'prefix': self.get_formset_class().get_default_prefix()
        })
        
        return kwargs
    
    def get_formset(self, formset_class=None) -> BaseFormSet:
        if formset_class is None:
            formset_class = self.get_formset_class()
        
        return formset_class(**self.get_formset_kwargs())

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
        context.update({
            'is_formset_row': True,
        })
        if 'formset' not in kwargs:
            context['formset'] = self.get_formset()
        
        return context
    
    def perolehan_nilai_ilo_graph(self, list_ilo: QuerySet[Ilo], is_multiple_result: bool, calculation_result: dict):
        json_response = {
            'labels': [ilo.nama for ilo in list_ilo],
            'datasets': [
                {
                    'label': 'Satisfactory Level',
                    'data': [ilo.satisfactory_level for ilo in list_ilo],
                    'fill': False,
                }
            ]
        }

        if is_multiple_result:
            # Update to bar chart
            json_response.update({
                'chart_type': 'bar'
            })
            # Update satisfactory level to line
            json_response['datasets'][0].update({
                'type': 'line'
            })
        else:
            json_response.update({
                'chart_type': 'radar'
            })

        for key, value in calculation_result.items():
            json_response['datasets'].append({
                'label': key,
                'data': [nilai_ilo for nama_ilo, nilai_ilo in value.items()],
                'fill': False,
            })

        return json.dumps(json_response)

    def form_valid(self, form, formset) -> HttpResponse:
        kurikulum_obj = form.cleaned_data.get('kurikulum')
        formset_cleaned_data = formset.cleaned_data

        # Get list ilo and max sks prodi
        list_ilo, max_sks_prodi = get_ilo_and_sks_from_kurikulum(kurikulum_obj)
        
        # Filter dict is based on tahun ajaran
        """
        filter_dict = {
            tahun_ajaran_prodi_id:[
                semester_prodi_id
            ],
        }
        """
        filter_dict = {}

        is_semester_included = len(formset_cleaned_data[0].get('semester', '').strip()) != 0

        # Separate tahun ajaran and semester
        for clean_data in formset.cleaned_data:
            tahun_ajaran_prodi_id = clean_data['tahun_ajaran']

            if tahun_ajaran_prodi_id not in filter_dict.keys():
                filter_dict[tahun_ajaran_prodi_id] = []
            
            if is_semester_included:
                semester_prodi_id = clean_data['semester']
                filter_dict[tahun_ajaran_prodi_id].append(semester_prodi_id)
        
        # If is multiple result, use line chart, else, use radar chart
        is_multiple_result = len(filter_dict.keys()) > 1

        is_success, message, result = process_filter_laporan_cpl(list_ilo, max_sks_prodi, is_semester_included, filter_dict)

        perolehan_nilai_ilo_graph = self.perolehan_nilai_ilo_graph(list_ilo, is_multiple_result, result)

        if is_success:
            messages.success(self.request, message)
        else:
            messages.error(self.request, message)

        return self.render_to_response(
            self.get_context_data(
                form=form, formset=formset,
                perolehan_nilai_ilo_graph=perolehan_nilai_ilo_graph,
            )
        )
    
    def form_invalid(self, form, formset) -> HttpResponse:
        return self.render_to_response(
            self.get_context_data(
                form=form, formset=formset
            )
        )
