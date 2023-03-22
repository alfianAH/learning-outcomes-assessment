import json
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.contrib import messages
from django.forms import BaseFormSet
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from mata_kuliah_semester.models import PesertaMataKuliah
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
    process_ilo_prodi,
    process_ilo_mahasiswa,
)


User = get_user_model()


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


class LaporanCapaianPembelajaranTemplateView(FormView):
    formset_class = None
    table_scroll_head_header: str = ''
    table_scroll_head_body: str = ''
    table_scroll_data_header: str = ''
    table_scroll_data_body: str = ''

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
            'table_scroll_head_header': self.table_scroll_head_header,
            'table_scroll_head_body': self.table_scroll_head_body,
            'table_scroll_data_header': self.table_scroll_data_header,
            'table_scroll_data_body': self.table_scroll_data_body,
        })
        if 'formset' not in kwargs:
            context['formset'] = self.get_formset()
        
        return context
    
    def form_valid(self, form, formset) -> HttpResponse:
        raise NotImplementedError
    
    def form_invalid(self, form, formset) -> HttpResponse:
        return self.render_to_response(
            self.get_context_data(
                form=form, formset=formset
            )
        )
    
    def show_result_messages(self, is_success: bool, message: str):
        if is_success:
            messages.success(self.request, message)
        else:
            messages.error(self.request, message)
    
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

        return json_response


class LaporanCapaianPembelajaranView(LaporanCapaianPembelajaranTemplateView):
    template_name = 'laporan-cpl/home.html'
    form_class = KurikulumChoiceForm
    formset_class = TahunAjaranSemesterFormset
    success_url = reverse_lazy('laporan_cpl:home')

    table_scroll_head_header: str = 'laporan-cpl/partials/prodi/table-scroll-head-header-prodi.html'
    table_scroll_head_body: str = 'laporan-cpl/partials/prodi/table-scroll-head-body-prodi.html'
    table_scroll_data_header: str = 'laporan-cpl/partials/prodi/table-scroll-data-header-prodi.html'
    table_scroll_data_body: str = 'laporan-cpl/partials/prodi/table-scroll-data-body-prodi.html'

    def perolehan_nilai_ilo_graph(self, list_ilo: QuerySet[Ilo], is_multiple_result: bool, calculation_result: dict):
        json_response = super().perolehan_nilai_ilo_graph(list_ilo, is_multiple_result, calculation_result)

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
        for clean_data in formset_cleaned_data:
            tahun_ajaran_prodi_id = clean_data['tahun_ajaran']

            if tahun_ajaran_prodi_id not in filter_dict.keys():
                filter_dict[tahun_ajaran_prodi_id] = []
            
            if is_semester_included:
                semester_prodi_id = clean_data['semester']
                filter_dict[tahun_ajaran_prodi_id].append(semester_prodi_id)
        
        filter = []
        if is_semester_included:
            # Semester filters
            for tahun_ajaran_prodi_id, list_semester_prodi_id in filter_dict.items():
                for semester_prodi_id in list_semester_prodi_id:
                    if not semester_prodi_id.strip(): continue

                    try:
                        semester_prodi_obj = SemesterProdi.objects.get(
                            id_neosia=semester_prodi_id
                        )
                    except SemesterProdi.DoesNotExist:
                        message = 'Semester Prodi (ID={}) tidak ada di database.'.format(semester_prodi_id)
                        if settings.DEBUG: print(message)
                        messages.error(self.request, message)
                        continue
                    except SemesterProdi.MultipleObjectsReturned:
                        message = 'Semester Prodi (ID={}) mengembalikan multiple object.'.format(semester_prodi_id)
                        if settings.DEBUG: print(message)
                        messages.error(self.request, message)
                        continue
                    
                    filter.append((semester_prodi_obj, str(semester_prodi_obj.semester)))

            # Filter peserta MK
            list_peserta_mk = PesertaMataKuliah.objects.filter(
                kelas_mk_semester__mk_semester__semester__in=[semester_prodi_obj for semester_prodi_obj, _ in filter]
            )
        else:
            # Tahun ajaran filters
            for tahun_ajaran_prodi_id in filter_dict.keys():
                if not tahun_ajaran_prodi_id.strip(): continue

                try:
                    tahun_ajaran_prodi_obj = TahunAjaranProdi.objects.get(
                        id=tahun_ajaran_prodi_id
                    )
                except TahunAjaranProdi.DoesNotExist:
                    message = 'TahunAjaranProdi (ID={}) tidak ada di database.'.format(tahun_ajaran_prodi_id)
                    if settings.DEBUG: print(message)
                    continue
                except TahunAjaranProdi.MultipleObjectsReturned:
                    message = 'TahunAjaranProdi (ID={}) mengembalikan multiple object.'.format(tahun_ajaran_prodi_id)
                    if settings.DEBUG: print(message)
                    continue
                
                filter.append((tahun_ajaran_prodi_obj, str(tahun_ajaran_prodi_obj.tahun_ajaran)))

            # Filter peserta MK
            list_peserta_mk = PesertaMataKuliah.objects.filter(
                kelas_mk_semester__mk_semester__semester__tahun_ajaran_prodi__in=[tahun_ajaran_prodi_obj for tahun_ajaran_prodi_obj, _ in filter]
            )

        # If is multiple result, use line chart, else, use radar chart
        is_multiple_result = len(filter) > 1

        # Process
        prodi_is_success, prodi_message, prodi_result = process_ilo_prodi(list_ilo, max_sks_prodi, is_semester_included, filter)
        mahasiswa_is_success, mahasiswa_message, mahasiswa_result = process_ilo_mahasiswa(list_ilo, max_sks_prodi, list_peserta_mk, is_semester_included, filter)

        perolehan_nilai_ilo_graph = self.perolehan_nilai_ilo_graph(list_ilo, is_multiple_result, prodi_result)

        # Success and Error messages
        self.show_result_messages(prodi_is_success, prodi_message)
        self.show_result_messages(mahasiswa_is_success, mahasiswa_message)

        return self.render_to_response(
            self.get_context_data(
                form=form, formset=formset,
                perolehan_nilai_ilo_graph=perolehan_nilai_ilo_graph,
                object_list=mahasiswa_result,
                list_ilo=list_ilo,
                list_filter=filter,
            )
        )


class LaporanCapaianPembelajaranMahasiswaView(LaporanCapaianPembelajaranTemplateView):
    template_name = 'laporan-cpl/laporan-mahasiswa.html'
    form_class = KurikulumChoiceForm
    formset_class = TahunAjaranSemesterFormset

    user: User = None
    
    table_scroll_head_header: str = 'laporan-cpl/partials/mahasiswa/table-scroll-head-header-mahasiswa.html'
    table_scroll_head_body: str = 'laporan-cpl/partials/mahasiswa/table-scroll-head-body-mahasiswa.html'
    table_scroll_data_header: str = 'laporan-cpl/partials/mahasiswa/table-scroll-data-header-mahasiswa.html'
    table_scroll_data_body: str = 'laporan-cpl/partials/mahasiswa/table-scroll-data-body-mahasiswa.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        
        username = kwargs.get('username')
        self.user = get_object_or_404(User, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user': self.user,
        })
        return context
    
    def perolehan_nilai_ilo_graph(self, list_ilo: QuerySet[Ilo], is_multiple_result: bool, calculation_result: dict):
        json_response = super().perolehan_nilai_ilo_graph(list_ilo, is_multiple_result, calculation_result)

        for _, data_mhs in calculation_result.items():
            for filter in data_mhs['result']:
                filter_name = filter['filter']
                filter_results = filter['result']

                json_response['datasets'].append({
                    'label': filter_name,
                    'data': [filter_result['nilai'] for filter_result in filter_results],
                    'fill': False,
                })

            break

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
        for clean_data in formset_cleaned_data:
            tahun_ajaran_prodi_id = clean_data['tahun_ajaran']

            if tahun_ajaran_prodi_id not in filter_dict.keys():
                filter_dict[tahun_ajaran_prodi_id] = []
            
            if is_semester_included:
                semester_prodi_id = clean_data['semester']
                filter_dict[tahun_ajaran_prodi_id].append(semester_prodi_id)
        
        filter = []
        if is_semester_included:
            # Semester filters
            for tahun_ajaran_prodi_id, list_semester_prodi_id in filter_dict.items():
                for semester_prodi_id in list_semester_prodi_id:
                    if not semester_prodi_id.strip(): continue

                    try:
                        semester_prodi_obj = SemesterProdi.objects.get(
                            id_neosia=semester_prodi_id
                        )
                    except SemesterProdi.DoesNotExist:
                        message = 'Semester Prodi (ID={}) tidak ada di database.'.format(semester_prodi_id)
                        if settings.DEBUG: print(message)
                        messages.error(self.request, message)
                        continue
                    except SemesterProdi.MultipleObjectsReturned:
                        message = 'Semester Prodi (ID={}) mengembalikan multiple object.'.format(semester_prodi_id)
                        if settings.DEBUG: print(message)
                        messages.error(self.request, message)
                        continue
                    
                    filter.append((semester_prodi_obj, str(semester_prodi_obj.semester)))

            # Filter peserta MK
            list_peserta_mk = PesertaMataKuliah.objects.filter(
                mahasiswa=self.user,
                kelas_mk_semester__mk_semester__semester__in=[semester_prodi_obj for semester_prodi_obj, _ in filter]
            )
        else:
            # Tahun ajaran filters
            for tahun_ajaran_prodi_id in filter_dict.keys():
                if not tahun_ajaran_prodi_id.strip(): continue

                try:
                    tahun_ajaran_prodi_obj = TahunAjaranProdi.objects.get(
                        id=tahun_ajaran_prodi_id
                    )
                except TahunAjaranProdi.DoesNotExist:
                    message = 'TahunAjaranProdi (ID={}) tidak ada di database.'.format(tahun_ajaran_prodi_id)
                    if settings.DEBUG: print(message)
                    continue
                except TahunAjaranProdi.MultipleObjectsReturned:
                    message = 'TahunAjaranProdi (ID={}) mengembalikan multiple object.'.format(tahun_ajaran_prodi_id)
                    if settings.DEBUG: print(message)
                    continue
                
                filter.append((tahun_ajaran_prodi_obj, str(tahun_ajaran_prodi_obj.tahun_ajaran)))

            # Filter peserta MK
            list_peserta_mk = PesertaMataKuliah.objects.filter(
                mahasiswa=self.user,
                kelas_mk_semester__mk_semester__semester__tahun_ajaran_prodi__in=[tahun_ajaran_prodi_obj for tahun_ajaran_prodi_obj, _ in filter]
            )
        
        # If is multiple result, use line chart, else, use radar chart
        is_multiple_result = len(filter) > 1

        mahasiswa_is_success, mahasiswa_message, mahasiswa_result = process_ilo_mahasiswa(list_ilo, max_sks_prodi, list_peserta_mk, is_semester_included, filter)

        perolehan_nilai_ilo_graph = self.perolehan_nilai_ilo_graph(list_ilo, is_multiple_result, mahasiswa_result)

        self.show_result_messages(mahasiswa_is_success, mahasiswa_message)

        return self.render_to_response(
            self.get_context_data(
                form=form, formset=formset,
                perolehan_nilai_ilo_graph=perolehan_nilai_ilo_graph,
            )
        )
