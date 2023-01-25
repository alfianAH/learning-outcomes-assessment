from django.http import HttpRequest, HttpResponse
from django.views.generic.list import ListView


class MyListView(ListView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        get_data = request.GET
        try:
            data_per_page = int(get_data.get('data_per_page'))
        except (ValueError, TypeError):
            data_per_page = None

        if data_per_page is not None:
            self.paginate_by = data_per_page
        return super().get(request, *args, **kwargs)
    