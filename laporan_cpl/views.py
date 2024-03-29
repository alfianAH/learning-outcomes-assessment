from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import (
    FileResponse, Http404, HttpResponse, 
    HttpRequest, JsonResponse
)
from django_q.tasks import async_task, result
from django_q.models import Task
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, View
from mata_kuliah_semester.models import PesertaMataKuliah
from learning_outcomes_assessment.forms.edit import MultiFormView
from learning_outcomes_assessment.auth.mixins import(
    MahasiswaAsPesertaMixin,
)
from pi_area.models import PerformanceIndicator
from semester.models import (
    TahunAjaranProdi,
    SemesterProdi,
)
from ilo.models import Ilo
from .forms import (
    KurikulumChoiceForm,
    TahunAjaranSemesterFormset,
    MataKuliahSemesterExcludeForm,
)
from .utils import (
    get_ilo_and_sks_from_kurikulum,
    generate_laporan_cpl_prodi_pdf,
    generate_laporan_cpl_prodi_raw,
    generate_laporan_cpl_mahasiswa_pdf,
    generate_laporan_cpl_per_mahasiswa_pdf,
    generate_laporan_cpl_per_mahasiswa_raw,
    generate_laporan_pi_pdf,
)
from .tasks import (
    process_ilo_prodi,
    process_ilo_mahasiswa,
    process_ilo_prodi_by_kurikulum,
    process_ilo_mahasiswa_by_kurikulum,
    process_pi,
    process_pi_by_kurikulum,
)


User = get_user_model()


# Create your views here.
class GetTahunAjaranJsonResponse(TemplateView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        selected_kurikulum_id = request.GET.get('kurikulum_id', '')
        username = request.GET.get('username', None)
        tahun_ajaran_choices = [('', '---------')]

        # If kurikulum_id is empty str or request is not AJAX, return
        if not selected_kurikulum_id.strip() or not request.is_ajax(): 
            return JsonResponse({'choices': tahun_ajaran_choices})
        
        if request.user.role != 'm':
            if username is None:
                tahun_ajaran_prodi_qs = TahunAjaranProdi.objects.filter(
                    semesterprodi__matakuliahsemester__mk_kurikulum__kurikulum__id_neosia=selected_kurikulum_id
                ).distinct()
            else:
                tahun_ajaran_prodi_qs = TahunAjaranProdi.objects.filter(
                    semesterprodi__matakuliahsemester__mk_kurikulum__kurikulum__id_neosia=selected_kurikulum_id,
                    semesterprodi__matakuliahsemester__kelasmatakuliahsemester__pesertamatakuliah__mahasiswa__username=username
                ).distinct()
        else:
            tahun_ajaran_prodi_qs = TahunAjaranProdi.objects.filter(
                semesterprodi__matakuliahsemester__mk_kurikulum__kurikulum__id_neosia=selected_kurikulum_id,
                semesterprodi__matakuliahsemester__kelasmatakuliahsemester__pesertamatakuliah__mahasiswa=request.user
            ).distinct()
        
        tahun_ajaran_choices += [(tahun_ajaran_prodi.pk, str(tahun_ajaran_prodi.tahun_ajaran)) for tahun_ajaran_prodi in tahun_ajaran_prodi_qs]

        return JsonResponse({'choices': tahun_ajaran_choices})
    

class GetSemesterJsonResponse(TemplateView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        selected_tahun_ajaran_id: str = request.GET.get('tahun_ajaran_id', '')
        username = request.GET.get('username', None)
        semester_choices = [('', '---------')]

        # If tahun_ajaran_id is empty str or request is not AJAX, return
        if not selected_tahun_ajaran_id.strip() or not request.is_ajax(): 
            return JsonResponse({'choices': semester_choices})
        
        if request.user.role != 'm':
            if username is None:
                semester_prodi_qs = SemesterProdi.objects.filter(
                    tahun_ajaran_prodi=selected_tahun_ajaran_id
                )
            else:
                semester_prodi_qs = SemesterProdi.objects.filter(
                    tahun_ajaran_prodi=selected_tahun_ajaran_id,
                    matakuliahsemester__kelasmatakuliahsemester__pesertamatakuliah__mahasiswa__username=username
                )
        else:
            semester_prodi_qs = SemesterProdi.objects.filter(
                tahun_ajaran_prodi=selected_tahun_ajaran_id,
                matakuliahsemester__kelasmatakuliahsemester__pesertamatakuliah__mahasiswa=request.user
            ).distinct()
        
        semester_choices += [(semester_prodi.pk, str(semester_prodi.semester.nama)) for semester_prodi in semester_prodi_qs]

        return JsonResponse({'choices': semester_choices})


class LaporanCapaianPembelajaranTemplateView(LoginRequiredMixin, MultiFormView):
    form_classes = {
        'kurikulum_form': KurikulumChoiceForm,
        'filter_formset': TahunAjaranSemesterFormset,
    }
    add_more_btn_text = 'Tambah filter'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['kurikulum_form'].update({
            'prodi': self.request.user.prodi,
        })
        kwargs['filter_formset'].update({
            'prefix': self.form_classes['filter_formset'].get_default_prefix()
        })
        return kwargs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'is_formset_row': True,
            'add_more_btn_text': self.add_more_btn_text,
        })
        
        return context
    
    def show_result_messages(self, is_success: bool, message: str):
        if is_success:
            messages.success(self.request, message)
        else:
            messages.error(self.request, message)


class LaporanCapaianPembelajaranView(LaporanCapaianPembelajaranTemplateView):
    template_name = 'laporan-cpl/home.html'
    success_url = reverse_lazy('laporan_cpl:home')

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.role == 'm':
            return redirect(request.user.get_laporan_cpl_url())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        time = timezone.now().strftime('%d%m%Y-%H%M%S')
        raw_cpl_prodi_filename = 'Laporan CPL Prodi RAW-{}.xlsx'.format(time)
        cpl_prodi_filename = 'Laporan CPL Prodi-{}.pdf'.format(time)
        cpl_mahasiswa_filename = 'Laporan CPL Mahasiwa-{}.pdf'.format(time)
        
        context.update({
            'cpl_prodi_filename': cpl_prodi_filename,
            'cpl_mahasiswa_filename': cpl_mahasiswa_filename,
            'raw_cpl_prodi_filename': raw_cpl_prodi_filename,
        })
        
        return context

    def forms_valid(self, forms: dict) -> HttpResponse:
        kurikulum_obj = forms['kurikulum_form'].cleaned_data.get('kurikulum')
        formset_cleaned_data = forms['filter_formset'].cleaned_data

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

        if len(formset_cleaned_data) == 0:
            is_multiple_result = False
            # Filter by kurikulum
            # Filter peserta MK
            list_peserta_mk = PesertaMataKuliah.objects.filter(
                kelas_mk_semester__mk_semester__mk_kurikulum__kurikulum=kurikulum_obj
            ).exclude(nilai_akhir=None)

            filter = [(kurikulum_obj, kurikulum_obj.nama)]
            
            # Process
            prodi_task = async_task(
                process_ilo_prodi_by_kurikulum,
                list_ilo, max_sks_prodi, filter, is_multiple_result
            )
            mahasiswa_task = async_task(
                process_ilo_mahasiswa_by_kurikulum,
                list_ilo, max_sks_prodi, filter, is_multiple_result, list_peserta_mk
            )
        else:
            # Filter by tahun ajaran or semester
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
                ).exclude(nilai_akhir=None)
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
                ).exclude(nilai_akhir=None)

            # If is multiple result, use line chart, else, use radar chart
            is_multiple_result = len(filter) > 1

            # Process
            prodi_task = async_task(
                process_ilo_prodi,
                list_ilo, max_sks_prodi, filter, is_multiple_result, is_semester_included
            )
            mahasiswa_task = async_task(
                process_ilo_mahasiswa,
                list_ilo, max_sks_prodi, filter, is_multiple_result, list_peserta_mk, is_semester_included
            )

        return self.render_to_response(
            self.get_context_data(
                forms=forms,
                prodi_task=prodi_task,
                mahasiswa_task=mahasiswa_task,
                list_ilo=list_ilo,
                list_filter=filter,
                is_multiple_result=is_multiple_result,
            )
        )


class ListMahasiswaLaporanCPLProgrmStudiView(TemplateView):
    template_name = 'laporan-cpl/partials/list-mahasiswa-prodi.html'
    table_scroll_head_header: str = 'laporan-cpl/partials/prodi/table-scroll-head-header-prodi.html'
    table_scroll_head_body: str = 'laporan-cpl/partials/prodi/table-scroll-head-body-prodi.html'
    table_scroll_data_header: str = 'laporan-cpl/partials/prodi/table-scroll-data-header-prodi.html'
    table_scroll_data_body: str = 'laporan-cpl/partials/prodi/table-scroll-data-body-prodi.html'
    mahasiswa_result = None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.is_ajax(): 
            raise PermissionDenied
        self.task_id = request.GET.get('task_id')
        if self.task_id is None: raise Http404
        
        # Get result
        task_result = result(self.task_id)
        if task_result is not None:
            _, _, self.mahasiswa_result, _ = task_result
        
        # Get filter list from task obj
        task_obj = Task.objects.get(id=self.task_id)
        self.list_filter = task_obj.args[2]
        self.list_ilo = task_obj.args[0]

        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'list_filter': self.list_filter,
            'list_ilo': self.list_ilo,
            'object_list': self.mahasiswa_result,
            'table_scroll_head_header': self.table_scroll_head_header,
            'table_scroll_head_body': self.table_scroll_head_body,
            'table_scroll_data_header': self.table_scroll_data_header,
            'table_scroll_data_body': self.table_scroll_data_body,
            'mahasiswa_task': self.task_id,
        })
        return context


class LaporanCapaianPembelajaranDownloadView(View):
    download_cpl_prodi = False
    download_cpl_mahasiswa = False

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        
        time = timezone.now().strftime('%d%m%Y-%H%M%S')
        self.cpl_prodi_filename = 'Laporan CPL Prodi-{}.pdf'.format(time)
        self.cpl_mahasiswa_filename = 'Laporan CPL Mahasiwa-{}.pdf'.format(time)

        if 'download_cpl' in request.GET:
            if request.GET.get('download_cpl') == 'prodi':
                self.download_cpl_prodi = True
            elif request.GET.get('download_cpl') == 'mahasiswa':
                self.download_cpl_mahasiswa = True

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.role == 'm': raise PermissionDenied
        if not request.is_ajax(): raise PermissionDenied
        
        task_id = request.GET.get('task_id')
        if task_id is None: raise PermissionDenied

        task_obj = Task.objects.get(id=task_id)

        list_ilo: QuerySet[Ilo] = task_obj.args[0]
        filter = task_obj.args[2]
        
        ilo_obj: Ilo = list_ilo.first()
        prodi = ilo_obj.get_kurikulum().prodi_jenjang.program_studi.nama
        fakultas = ilo_obj.get_kurikulum().prodi_jenjang.program_studi.fakultas.nama

        # Process
        if self.download_cpl_prodi:
            prodi_is_success, prodi_message, prodi_result, _ = result(task_id)

            if prodi_is_success:
                file = generate_laporan_cpl_prodi_pdf(list_ilo, filter, prodi_result, prodi, fakultas)
                if settings.DEBUG: print('Berhasil generate file laporan CPL prodi.')
                return self.download_laporan_cpl(file, self.cpl_prodi_filename)
            else:
                if settings.DEBUG: print(prodi_message)
                return HttpResponse(prodi_message)
        
        if self.download_cpl_mahasiswa:
            mahasiswa_is_success, mahasiswa_message, mahasiswa_result, _ = result(task_id)

            if mahasiswa_is_success:
                file = generate_laporan_cpl_mahasiswa_pdf(list_ilo, filter, mahasiswa_result, prodi, fakultas)
                if settings.DEBUG: print('Berhasil generate file laporan CPL mahasiswa.')
                return self.download_laporan_cpl(file, self.cpl_prodi_filename)
            else:
                if settings.DEBUG: print(mahasiswa_message)
                return HttpResponse(mahasiswa_message)
        
        return HttpResponse('Empty')
    
    def download_laporan_cpl(self, file, filename):
        as_attachment = True
        response = FileResponse(file, as_attachment=as_attachment, filename=filename)
        return response


class LaporanCapaianPembelajaranRawDownloadView(View):
    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        
        time = timezone.now().strftime('%d%m%Y-%H%M%S')
        self.cpl_prodi_filename = 'Laporan CPL Prodi Raw-{}.xlsx'.format(time)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.role == 'm': raise PermissionDenied
        if not request.is_ajax(): raise PermissionDenied
        
        task_id = request.GET.get('task_id')
        if task_id is None: raise PermissionDenied

        task_obj = Task.objects.get(id=task_id)

        list_ilo: QuerySet[Ilo] = task_obj.args[0]
        max_sks_prodi = task_obj.args[1]
        filter = task_obj.args[2]
        if task_obj.func == 'laporan_cpl.tasks.process_ilo_prodi':
            is_kurikulum = False
            is_semester_included: bool = task_obj.args[-1]
        elif task_obj.func == 'laporan_cpl.tasks.process_ilo_prodi_by_kurikulum':
            is_kurikulum = True
            is_semester_included = False

        prodi_is_success, prodi_message, _, _ = result(task_id)

        if prodi_is_success:
            file = generate_laporan_cpl_prodi_raw(list_ilo, max_sks_prodi, filter, is_kurikulum, is_semester_included)
            if settings.DEBUG: print('Berhasil generate RAW file laporan CPL prodi.')
            return self.download_laporan_cpl(file, self.cpl_prodi_filename)
        else:
            if settings.DEBUG: print(prodi_message)
            return HttpResponse(prodi_message)

    def download_laporan_cpl(self, file, filename):
        as_attachment = True
        response = FileResponse(file, as_attachment=as_attachment, filename=filename)
        return response


class LaporanCapaianPembelajaranMahasiswaView(MahasiswaAsPesertaMixin, LaporanCapaianPembelajaranTemplateView):
    template_name = 'laporan-cpl/laporan-mahasiswa.html'
    form_classes = {
        'kurikulum_form': KurikulumChoiceForm,
        'filter_formset': TahunAjaranSemesterFormset,
        'mk_filter_form': MataKuliahSemesterExcludeForm,
    }
    
    list_item_name: str = 'laporan-cpl/partials/mahasiswa/list-item-name.html'
    list_custom_field_template: str = 'laporan-cpl/partials/mahasiswa/list-custom-field-mahasiswa.html'
    table_custom_field_header_template: str = 'laporan-cpl/partials/mahasiswa/table-custom-field-header-mahasiswa.html'
    table_custom_field_template: str = 'laporan-cpl/partials/mahasiswa/table-custom-field-mahasiswa.html'

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        username = kwargs.get('username')
        self.user = get_object_or_404(User, username=username)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user_dict = {
            'user': self.user
        }
        if self.user.role == 'm':
            kwargs['kurikulum_form'].update(user_dict)
            kwargs['filter_formset'].update(user_dict)

        kwargs['mk_filter_form'].update(user_dict)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        time = timezone.now().strftime('%d%m%Y-%H%M%S')
        cpl_mahasiswa_filename = 'Laporan CPL Mahasiwa-{}-{}.pdf'.format(self.user.username, time)
        raw_cpl_mahasiswa_filename = 'Laporan CPL Mahasiwa RAW-{}-{}.xlsx'.format(self.user.username, time)

        context.update({
            'user': self.user,
            'list_item_name': self.list_item_name,
            'list_custom_field_template': self.list_custom_field_template,
            'table_custom_field_header_template': self.table_custom_field_header_template,
            'table_custom_field_template': self.table_custom_field_template,
            'cpl_mahasiswa_filename': cpl_mahasiswa_filename,
            'raw_cpl_mahasiswa_filename': raw_cpl_mahasiswa_filename,
        })
        return context
    
    def forms_valid(self, forms: dict) -> HttpResponse:
        kurikulum_obj = forms['kurikulum_form'].cleaned_data.get('kurikulum')
        formset_cleaned_data = forms['filter_formset'].cleaned_data
        mk_filter_cleaned_data = forms['mk_filter_form'].cleaned_data.get('mk_semester', [])

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
        
        if len(formset_cleaned_data) == 0:
            is_multiple_result = False
            filter = [(kurikulum_obj, kurikulum_obj.nama)]

            # Filter by kurikulum
            # Filter peserta MK
            list_peserta_mk = PesertaMataKuliah.objects.filter(
                mahasiswa=self.user,
                kelas_mk_semester__mk_semester__mk_kurikulum__kurikulum=kurikulum_obj
            ).exclude(nilai_akhir=None).exclude(
                id_neosia__in=mk_filter_cleaned_data
            )

            mahasiswa_task = async_task(
                process_ilo_mahasiswa_by_kurikulum,
                list_ilo, max_sks_prodi, filter, is_multiple_result, list_peserta_mk
            )
        else:
            # Filter by tahun ajaran or semester
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
                ).exclude(nilai_akhir=None).exclude(
                    id_neosia__in=mk_filter_cleaned_data
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
                ).exclude(nilai_akhir=None).exclude(
                    id_neosia__in=mk_filter_cleaned_data
                )
            
            # If is multiple result, use line chart, else, use radar chart
            is_multiple_result = len(filter) > 1

            mahasiswa_task = async_task(
                process_ilo_mahasiswa,
                list_ilo, max_sks_prodi, filter, is_multiple_result, list_peserta_mk, is_semester_included
            )

        return self.render_to_response(
            self.get_context_data(
                forms=forms,
                mahasiswa_task=mahasiswa_task,
                options=list_peserta_mk,
                list_ilo=list_ilo,
            )
        )


class LaporanCapaianPembelajaranMahasiswaDownloadView(MahasiswaAsPesertaMixin, View):
    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        username = kwargs.get('username')
        self.user = get_object_or_404(User, username=username)
        time = timezone.now().strftime('%d%m%Y-%H%M%S')
        self.cpl_mahasiswa_filename = 'Laporan CPL Mahasiwa-{}-{}.pdf'.format(username, time)

        self.user = get_object_or_404(User, username=username)
    
    def download_laporan_cpl(self, file, filename):
        as_attachment = True
        response = FileResponse(file, as_attachment=as_attachment, filename=filename)
        return response
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.is_ajax(): raise PermissionDenied
        
        task_id = request.GET.get('task_id')
        if task_id is None: raise PermissionDenied

        task_obj = Task.objects.get(id=task_id)

        list_ilo: QuerySet[Ilo] = task_obj.args[0]
        filter = task_obj.args[2]
        list_peserta_mk = task_obj.args[4]
        
        ilo_obj: Ilo = list_ilo.first()
        prodi = ilo_obj.get_kurikulum().prodi_jenjang.program_studi.nama
        fakultas = ilo_obj.get_kurikulum().prodi_jenjang.program_studi.fakultas.nama

        mahasiswa_is_success, mahasiswa_message, mahasiswa_result, _ = result(task_id)

        if mahasiswa_is_success:
            file = generate_laporan_cpl_per_mahasiswa_pdf(
                list_ilo, list_peserta_mk, filter, mahasiswa_result, self.user, prodi, fakultas)
            if settings.DEBUG: print('Berhasil generate file laporan CPL mahasiswa.')
            return self.download_laporan_cpl(file, self.cpl_mahasiswa_filename)
        else:
            if settings.DEBUG: print(mahasiswa_message)
            return HttpResponse(mahasiswa_message, status=404)


class LaporanCapaianPembelajaranMahasiswaRawDownloadView(MahasiswaAsPesertaMixin, View):
    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        username = kwargs.get('username')
        self.user = get_object_or_404(User, username=username)
        time = timezone.now().strftime('%d%m%Y-%H%M%S')
        self.cpl_mahasiswa_filename = 'Laporan CPL Mahasiwa-{}-{}.xlsx'.format(username, time)

        self.user = get_object_or_404(User, username=username)
    
    def download_laporan_cpl(self, file, filename):
        as_attachment = True
        response = FileResponse(file, as_attachment=as_attachment, filename=filename)
        return response
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.is_ajax(): raise PermissionDenied
        
        task_id = request.GET.get('task_id')
        if task_id is None: raise PermissionDenied

        task_obj = Task.objects.get(id=task_id)

        # Get all data for laporan CPL
        list_ilo: QuerySet[Ilo] = task_obj.args[0]
        max_sks_prodi = task_obj.args[1]
        filter = task_obj.args[2]
        if task_obj.func == 'laporan_cpl.tasks.process_ilo_mahasiswa':
            is_kurikulum = False
            is_semester_included: bool = task_obj.args[-1]
        elif task_obj.func == 'laporan_cpl.tasks.process_ilo_mahasiswa_by_kurikulum':
            is_kurikulum = True
            is_semester_included = False
        list_peserta_mk = task_obj.args[4]

        mahasiswa_is_success, mahasiswa_message, _, _ = result(task_id)

        if mahasiswa_is_success:
            file = generate_laporan_cpl_per_mahasiswa_raw(
                list_ilo, max_sks_prodi, list_peserta_mk, filter, is_kurikulum, is_semester_included)
            if settings.DEBUG: print('Berhasil generate file laporan CPL mahasiswa.')
            return self.download_laporan_cpl(file, self.cpl_mahasiswa_filename)
        else:
            if settings.DEBUG: print(mahasiswa_message)
            return HttpResponse(mahasiswa_message, status=404)


class LaporanPerformanceIndicatorView(LaporanCapaianPembelajaranTemplateView):
    template_name = 'laporan-cpl/laporan-pi.html'
    success_url = reverse_lazy('laporan_cpl:laporan_pi')

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.role == 'm': raise PermissionDenied
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        time = timezone.now().strftime('%d%m%Y-%H%M%S')
        pi_prodi_filename = 'Laporan PI Prodi-{}.pdf'.format(time)
        
        context.update({
            'pi_prodi_filename': pi_prodi_filename,
        })
        
        return context

    def forms_valid(self, forms: dict) -> HttpResponse:
        kurikulum_obj = forms['kurikulum_form'].cleaned_data.get('kurikulum')
        formset_cleaned_data = forms['filter_formset'].cleaned_data

        list_pi: QuerySet[PerformanceIndicator] = PerformanceIndicator.objects.filter(
            pi_area__assessment_area__kurikulum=kurikulum_obj
        ).distinct()
        
        # Filter dict is based on tahun ajaran
        """
        filter_dict = {
            tahun_ajaran_prodi_id:[
                semester_prodi_id
            ],
        }
        """
        filter_dict = {}

        if len(formset_cleaned_data) == 0:
            # Filter by kurikulum
            filter = [(kurikulum_obj, kurikulum_obj.nama)]
            
            # Process
            pi_task = async_task(
                process_pi_by_kurikulum,
                list_pi, filter
            )
        else:
            # Filter by tahun ajaran or semester
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

            # Process
            pi_task = async_task(
                process_pi,
                list_pi, filter, is_semester_included
            )

        return self.render_to_response(
            self.get_context_data(
                forms=forms,
                pi_task=pi_task,
                list_filter=filter,
            )
        )


class ListPiLaporanPiView(TemplateView):
    template_name = 'laporan-cpl/partials/list-pi.html'
    table_scroll_head_header: str = 'laporan-cpl/partials/pi/table-scroll-head-header-pi.html'
    table_scroll_head_body: str = 'laporan-cpl/partials/pi/table-scroll-head-body-pi.html'
    table_scroll_data_header: str = 'laporan-cpl/partials/pi/table-scroll-data-header-pi.html'
    table_scroll_data_body: str = 'laporan-cpl/partials/pi/table-scroll-data-body-pi.html'
    pi_result = None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.is_ajax(): 
            raise PermissionDenied
        self.task_id = request.GET.get('task_id')
        if self.task_id is None: raise Http404
        
        # Get result
        task_result = result(self.task_id)
        if task_result is not None:
            _, _, self.pi_result = task_result
        
        # Get filter list from task obj
        task_obj = Task.objects.get(id=self.task_id)
        self.list_filter = task_obj.args[1]
        self.list_pi = task_obj.args[0]

        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'list_filter': self.list_filter,
            'list_pi': self.list_pi,
            'object_list': self.pi_result,
            'table_scroll_head_header': self.table_scroll_head_header,
            'table_scroll_head_body': self.table_scroll_head_body,
            'table_scroll_data_header': self.table_scroll_data_header,
            'table_scroll_data_body': self.table_scroll_data_body,
            'pi_task': self.task_id,
        })
        return context


class LaporanPiDownloadView(View):
    download_pi = False

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        
        time = timezone.now().strftime('%d%m%Y-%H%M%S')
        self.pi_filename = 'Laporan CPL Prodi-{}.pdf'.format(time)

        if 'download_pi' in request.GET:
            self.download_pi = True

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.role == 'm': raise PermissionDenied
        if not request.is_ajax(): raise PermissionDenied
        
        task_id = request.GET.get('task_id')
        if task_id is None: raise PermissionDenied

        task_obj = Task.objects.get(id=task_id)

        list_pi: QuerySet[PerformanceIndicator] = task_obj.args[0]
        filter = task_obj.args[1]
        
        kurikulum_obj = list_pi.first().pi_area.assessment_area.kurikulum
        prodi = kurikulum_obj.prodi_jenjang.program_studi.nama
        fakultas = kurikulum_obj.prodi_jenjang.program_studi.fakultas.nama

        # Process
        if self.download_pi:
            is_success, message, pi_result = result(task_id)

            if is_success:
                file = generate_laporan_pi_pdf(list_pi, filter, pi_result, prodi, fakultas)
                if settings.DEBUG: print('Berhasil generate file laporan CPL prodi.')
                return self.download_laporan_cpl(file, self.pi_filename)
            else:
                if settings.DEBUG: print(message)
                return HttpResponse(message)
        
        return HttpResponse('Empty')
    
    def download_laporan_cpl(self, file, filename):
        as_attachment = True
        response = FileResponse(file, as_attachment=as_attachment, filename=filename)
        return response