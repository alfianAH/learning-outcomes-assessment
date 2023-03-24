from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.forms import BaseForm
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.edit import FormView


class ModelBulkDeleteView(FormView):
    model = None
    id_list_obj: str = ''
    success_msg: str = ''
    queryset = None

    def get_list_selected_obj(self):
        list_obj_id = self.request.POST.getlist(self.id_list_obj)
        list_obj_id = [*set(list_obj_id)]
        return list_obj_id

    def get_queryset(self):
        if self.queryset is not None:
            queryset = self.queryset
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        return queryset

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        list_obj_id = self.get_list_selected_obj()

        if len(list_obj_id) > 0:
            self.get_queryset().delete()
            messages.success(self.request, self.success_msg)
        
        return redirect(self.success_url)


class ModelBulkUpdateView(FormView):
    back_url: str = ''
    form_field_name: str = 'update_data'
    search_placeholder: str = 'Cari ...'
    submit_text: str = 'Update'
    no_choices_msg: str = 'Data sudah sinkron dengan data di Neosia'
    choices = []

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = self.get_form(form_class=self.form_class)
        
        if len(form.fields.get(self.form_field_name).choices) == 0:
            messages.info(request, self.no_choices_msg)
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)
    
    def get_form(self, form_class = None) -> BaseForm:
        form = super().get_form(form_class)
        
        form.fields[self.form_field_name].choices = self.choices
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'search_placeholder': self.search_placeholder,
            'back_url': self.back_url,
            'submit_text': self.submit_text,
        })
        return context


class DuplicateFormview(FormView):
    choices = []
    empty_choices_msg: str = 'Pilihan tidak ada'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if len(self.choices) == 0:
            messages.info(self.request, self.empty_choices_msg)
            return redirect(self.success_url)

        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'choices': self.choices
        })
        return kwargs


class MultiFormView(FormView):
    form_classes = {}

    def are_forms_valid(self, forms: dict):
        """
        Check if all forms defined in `form_classes` are valid.
        """
        for form in forms.values():
            if not form.is_valid():
                return False
        return True

    def forms_valid(self, forms: dict):
        """
        Redirects to get_success_url().
        """
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, forms: dict):
        """
        Renders a response containing the form errors.
        """
        return self.render_to_response(self.get_context_data(forms=forms))

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the forms.
        """
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        """
        Add forms into the context dictionary.
        """
        context = {}
        if 'forms' not in kwargs:
            context['forms'] = self.get_forms()
        else:
            context['forms'] = kwargs['forms']
        return context

    def get_forms(self):
        """
        Initializes the forms defined in `form_classes` with initial data from `get_initial()` and
        kwargs from get_form_kwargs().
        """
        forms = {}
        initial = self.get_initial()
        form_kwargs = self.get_form_kwargs()

        for key, form_class in self.form_classes.items():
            forms[key] = form_class(
                initial=initial[key], 
                **form_kwargs[key]
            )
        return forms

    def get_form_kwargs(self):
        """
        Build the keyword arguments required to instantiate the form.
        """

        kwargs = {}
        for key in self.form_classes.keys():
            if self.request.method in ('POST', 'PUT'):
                kwargs[key] = {
                    'data': self.request.POST,
                    'files': self.request.FILES,
                }
            else:
                kwargs[key] = {}
        return kwargs

    def get_initial(self):
        """
        Returns a copy of `initial` with empty initial data dictionaries for each form.
        """
        initial = super(MultiFormView, self).get_initial()
        for key in self.form_classes.keys():
            initial[key] = {}
        return initial

    def post(self, request, **kwargs):
        """
        Uses `are_forms_valid()` to call either `forms_valid()` or * `forms_invalid()`.
        """
        forms = self.get_forms()
        if self.are_forms_valid(forms):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)


class MultiModelFormView(MultiFormView):
    """
    View to handle multiple model form classes.
    """

    def forms_valid(self, forms: dict):
        """
        Calls `save()` on each form.
        """
        for form in forms.values():
            form.save()
        return super(MultiModelFormView, self).forms_valid(forms)

    def get_forms(self):
        """
        Initializes the forms defined in `form_classes` with initial data from `get_initial()`,
        kwargs from get_form_kwargs() and form instance object from `get_objects()`.
        """
        forms = {}
        objects = self.get_objects()
        initial = self.get_initial()
        form_kwargs = self.get_form_kwargs()

        for key, form_class in self.form_classes.items():
            forms[key] = form_class(
                instance=objects[key], 
                initial=initial[key], 
                **form_kwargs[key]
            )
        return forms

    def get_objects(self):
        """
        Returns dictionary with the instance objects for each form. Keys should match the
        corresponding form.
        """
        objects = {}
        for key in self.form_classes.keys():
            objects[key] = None
        return objects
