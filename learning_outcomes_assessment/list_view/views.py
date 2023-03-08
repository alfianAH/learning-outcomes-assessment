from django.forms import BaseForm
from django.http import Http404, HttpRequest
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext as _
from .list import MyListView


class ListViewModelA(MyListView):
    """List view model A
        * List view (small screen size, xs-sm)
        * Table view (large screen size, >= md)
        * Table strip
        * Checkbox
        * Badge
        * Open button
    """
    
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
    table_footer_custom_field_template: str = ''
    filter_template: str = ''
    sort_template: str = ''

    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)

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

        if self.update_context(self.table_footer_custom_field_template):
            context['table_footer_custom_field_template'] = self.table_footer_custom_field_template

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
    

class ListViewModelD(ListViewModelA):
    """List View Model D

    List view with expand button
        * List view (small screen, xs-sm)
        * Table view (large screen, >= md)
        * Table strip
        * Table without strip on the expand
        * Checkbox
        * Badge
        * Expand button
        * Action button
    """
    
    table_custom_expand_field_template: str = ''
    list_custom_expand_field_template: str = ''
    list_edit_template: str = ''
    list_item_name: str = 'components/list-table-view/model-d/list-item-name.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.update_context(self.list_custom_expand_field_template):
            context['list_custom_expand_field_template'] = self.list_custom_expand_field_template

        if self.update_context(self.table_custom_expand_field_template):
            context['table_custom_expand_field_template'] = self.table_custom_expand_field_template

        if self.update_context(self.list_edit_template):
            context['list_edit_template'] = self.list_edit_template
        
        return context


class DetailWithListViewMixin():
    single_model = None
    single_slug_field = 'slug'
    single_pk_url_kwarg: str = 'pk'
    context_object_name = None
    single_slug_url_kwarg: str = 'slug'
    single_queryset = None
    single_query_pk_and_slug = False

    def get_single_object(self, queryset=None):
        """
        Return the object the view is displaying.

        Require `self.queryset` and a `pk` or `slug` argument in the URLconf.
        Subclasses can override this to return any object.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_single_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.single_pk_url_kwarg)
        slug = self.kwargs.get(self.single_slug_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.single_query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_single_queryset(self):
        """
        Return the `QuerySet` that will be used to look up the object.

        This method is called by the default implementation of get_object() and
        may not be called if get_object() is overridden.
        """
        if self.single_queryset is None:
            if self.single_model:
                return self.single_model._default_manager.all()
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.model, %(cls)s.queryset, or override "
                    "%(cls)s.get_queryset()." % {
                        'cls': self.__class__.__name__
                    }
                )
        return self.single_queryset.all()

    def get_slug_field(self):
        """Get the name of a slug field to be used to look up by slug."""
        return self.single_slug_field


class DetailWithListViewModelA(DetailWithListViewMixin, ListViewModelA):
    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.single_object = self.get_single_object()

    def get_context_data(self, **kwargs):
        """Insert the single object into the context dict."""
        context = super().get_context_data()
        if self.single_object:
            context['single_object'] = self.single_object
        
        return context


class DetailWithListViewModelD(DetailWithListViewMixin, ListViewModelD):
    def setup(self, request: HttpRequest, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.single_object = self.get_single_object()

    def get_context_data(self, **kwargs):
        """Insert the single object into the context dict."""
        context = super().get_context_data()
        if self.single_object:
            context['single_object'] = self.single_object
        
        return context
