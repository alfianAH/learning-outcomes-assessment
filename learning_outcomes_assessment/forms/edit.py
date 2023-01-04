from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
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
