from django.forms import BaseForm
from .list import MyListView


class ListViewModelA(MyListView):
    filter_form = None
    sort_form: BaseForm = None
    sort_form_ordering_by_key: str = ''

    bulk_delete_url: str = ''
    reset_url: str = ''
    list_prefix_id: str = 'list-prefix-'
    list_item_name: str = 'components/list-table-view/model-a/list-item-name.html'
    list_id: str = 'list-content'
    input_name: str = 'id_'
    badge_template: str = ''
    list_custom_field_template: str = ''
    table_custom_field_header_template: str = ''
    table_custom_field_template: str = ''
    filter_template: str = ''
    sort_template: str = ''

    def get_ordering(self):
        if self.sort_form is None:
            return super().get_ordering()
        
        if self.sort_form.is_valid():
            self.ordering = self.sort_form.cleaned_data.get(
                self.sort_form_ordering_by_key, self.ordering
            )
        return super().get_ordering()

    def get_queryset(self):
        if self.filter_form is not None:
            self.queryset = self.filter_form.qs

        return super().get_queryset()

    def update_context(self, value) -> bool:
        if isinstance(value, str):
            if not value.strip(): return False
        else:
            if value is None: return False
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'bulk_delete_url': self.bulk_delete_url,
            'id': self.list_id,
            'input_name': self.input_name,
            'reset_url': self.reset_url,
            'list_prefix_id': self.list_prefix_id,
            'list_item_name': self.list_item_name,
            'list_custom_field_template': self.list_custom_field_template,
            'table_custom_field_header_template': self.table_custom_field_header_template,
            'table_custom_field_template': self.table_custom_field_template,
        })

        if self.update_context(self.badge_template):
            context['badge_template'] = self.badge_template

        if self.update_context(self.filter_template):
            context['filter_template'] = self.filter_template

        if self.update_context(self.sort_template):
            context['sort_template'] = self.sort_template

        if self.update_context(self.filter_form):
            context['filter_form'] = self.filter_form.form
            context['data_exist'] = True

        if self.update_context(self.sort_form):
            context['sort_form'] = self.sort_form
        
        return context
