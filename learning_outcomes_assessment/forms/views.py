import json
from django.contrib import messages
from django.forms import BaseInlineFormSet, BaseModelForm
from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic.edit import ProcessFormView, ModelFormMixin
from django.views.generic.detail import SingleObjectTemplateResponseMixin


class BaseHtmxFormView(ModelFormMixin, ProcessFormView):
    modal_title: str = 'Modal Title'
    modal_id: str = 'modal-id'
    button_text: str = 'Submit'
    post_url: str = ''
    success_msg: str = 'Berhasil menambahkan'
    error_msg: str = 'Gagal menambahkan'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if '/hx' in request.get_full_path():
            if not request.htmx: raise Http404
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'modal_title': self.modal_title,
            'modal_id': self.modal_id,
            'button_text': self.button_text,
            'post_url': self.post_url,
        })
        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, self.success_msg)
        return super().form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        form_errors = json.dumps(form.errors.as_json())
        error_message = '{}. Error: {}'.format(self.error_msg, form_errors)

        messages.error(self.request, error_message)
        return super().form_invalid(form)


class HtmxCreateFormView(SingleObjectTemplateResponseMixin, BaseHtmxFormView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = None
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = None
        return super().post(request, *args, **kwargs)


class HtmxUpdateFormView(SingleObjectTemplateResponseMixin,BaseHtmxFormView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class HtmxCreateInlineFormsetView(HtmxCreateFormView):
    id_total_form: str = '#id-TOTAL_FORMS'
    add_more_btn_text: str = 'Tambah lagi'
    formset_class: type[BaseInlineFormSet] = None
    formset: BaseInlineFormSet = None

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.formset = self.formset_class()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'id_total_form': self.id_total_form,
            'add_more_btn_text': self.add_more_btn_text,
            'formset': self.formset,
        })
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form()
        self.formset = self.formset_class(request.POST)

        if all([self.formset.is_valid(), form.is_valid()]):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, self.error_msg)
        return self.render_to_response(self.get_context_data(form=form))


class HtmxUpdateInlineFormsetView(HtmxUpdateFormView):
    id_total_form: str = '#id-TOTAL_FORMS'
    add_more_btn_text: str = 'Tambah lagi'
    formset_class: type[BaseInlineFormSet] = None
    formset: BaseInlineFormSet = None

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.object = self.get_object()

        self.formset = self.formset_class(
            instance=self.object
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'id_total_form': self.id_total_form,
            'add_more_btn_text': self.add_more_btn_text,
            'formset': self.formset,
        })
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form()
        self.formset = self.formset_class(
            request.POST,
            instance=self.object,
        )

        if all([self.formset.is_valid(), form.is_valid()]):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.save()
        self.formset.save(True)

        return super().form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, self.error_msg)
        return self.render_to_response(self.get_context_data(form=form))
