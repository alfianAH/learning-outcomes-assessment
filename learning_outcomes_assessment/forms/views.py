import json
from django.contrib import messages
from django.forms import BaseInlineFormSet, BaseModelForm
from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic.edit import ProcessFormView, ModelFormMixin
from django.views.generic.detail import SingleObjectTemplateResponseMixin


# Mixins
class MyModelFormMixin(ModelFormMixin):
    button_text: str = 'Submit'
    post_url: str = ''
    success_msg: str = 'Berhasil menambahkan'
    error_msg: str = 'Gagal menambahkan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
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


class HtmxModelFormMixin(MyModelFormMixin):
    modal_title: str = 'Modal Title'
    modal_content_id: str = 'modal-content'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'modal_title': self.modal_title,
            'modal_content_id': self.modal_content_id,
        })
        return context


class InlineFormsetModelForm():
    id_total_form: str = '#id-TOTAL_FORMS'
    add_more_btn_text: str = 'Tambah lagi'
    formset_class: type[BaseInlineFormSet] = None
    formset: BaseInlineFormSet = None


class InlineFormsetModelFormMixin(MyModelFormMixin, InlineFormsetModelForm):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'id_total_form': self.id_total_form,
            'add_more_btn_text': self.add_more_btn_text,
            'formset': self.formset,
        })
        return context

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(self.request, self.error_msg)
        return self.render_to_response(self.get_context_data(form=form))


class HtmxInlineFormsetModelFormMixin(HtmxModelFormMixin, InlineFormsetModelFormMixin):
    pass


class UpdateInlineFormsetModelFormMixin(InlineFormsetModelFormMixin):
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.save(commit=True)
        self.formset.save(commit=True)
        return super().form_valid(form)


class HtmxUpdateInlineFormsetModelFormMixin(
    HtmxInlineFormsetModelFormMixin,
    UpdateInlineFormsetModelFormMixin
):
    pass


# Process views
class HtmxProcessView(ProcessFormView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if '/hx' in request.get_full_path():
            if not request.htmx: raise Http404
        
        return super().get(request, *args, **kwargs)


# Base views
class BaseCreateInlineFormsetView(
    InlineFormsetModelFormMixin, ProcessFormView
):
    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.formset = self.formset_class()
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = None
        return super().get(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form()
        self.formset = self.formset_class(request.POST)
        
        if all([self.formset.is_valid(), form.is_valid()]):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class BaseUpdateInlineFormsetView(
    UpdateInlineFormsetModelFormMixin, ProcessFormView
):
    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        
        self.object = self.get_object()
        self.formset = self.formset_class(
            instance=self.object
        )
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        form = self.get_form()
        self.formset = self.formset_class(
            request.POST,
            instance=self.object
        )
        
        if all([self.formset.is_valid(), form.is_valid()]):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class BaseHtmxFormView(HtmxModelFormMixin, HtmxProcessView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = None
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = None
        return super().post(request, *args, **kwargs)


class BaseHtmxUpdateFormView(HtmxModelFormMixin, HtmxProcessView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class BaseHtmxCreateInlineFormsetView(
    HtmxInlineFormsetModelFormMixin, HtmxProcessView
):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.formset = self.formset_class()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = None
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form()
        self.formset = self.formset_class(request.POST)
        
        if all([self.formset.is_valid(), form.is_valid()]):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class BaseHtmxUpdateInlineFormsetView(
    HtmxUpdateInlineFormsetModelFormMixin, HtmxProcessView
):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

        self.object = self.get_object()
        self.formset = self.formset_class(
            instance=self.object
        ) 
    
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        form = self.get_form()
        self.formset = self.formset_class(
            request.POST,
            instance=self.object
        )
        
        if all([self.formset.is_valid(), form.is_valid()]):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


# Views
class UpdateInlineFormsetView(SingleObjectTemplateResponseMixin, BaseUpdateInlineFormsetView):
    pass


class HtmxCreateFormView(SingleObjectTemplateResponseMixin, BaseHtmxFormView):
    pass


class HtmxUpdateFormView(SingleObjectTemplateResponseMixin, BaseHtmxUpdateFormView):
    pass


class HtmxCreateInlineFormsetView(
    SingleObjectTemplateResponseMixin,
    BaseHtmxCreateInlineFormsetView
):
    pass


class HtmxUpdateInlineFormsetView(
    SingleObjectTemplateResponseMixin,
    BaseHtmxUpdateInlineFormsetView
):
    pass
