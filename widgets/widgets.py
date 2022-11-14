from django.forms import CheckboxSelectMultiple

class ChoiceListInteractive(CheckboxSelectMultiple):
    is_required: bool = False
    input_type: str = 'checkbox'
    template_name: str = 'custom-widgets/forms/widgets/checkbox-select-list-item-model-a.html'
    option_template_name: str = 'custom-widgets/forms/widgets/checkbox-option.html'
    badge_template: str = None
    list_custom_field_template: str = None
    table_custom_field_template: str = None
    table_custom_field_header_template: str = None

    def __init__(self, 
        badge_template: str = None, 
        list_custom_field_template: str = None, 
        table_custom_field_template: str = None,
        table_custom_field_header_template: str = None,
        *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.badge_template = badge_template or None
        self.list_custom_field_template = list_custom_field_template or None
        self.table_custom_field_template = table_custom_field_template or None
        self.table_custom_field_header_template = table_custom_field_header_template or None

    def create_option(self, *args, **kwargs):
        option = super().create_option(*args, **kwargs)
        
        # Add badget template
        if self.badge_template is not None:
            option['badge_template'] = self.badge_template
        
        # Add custom field template for list
        if self.list_custom_field_template is not None:
            option['list_custom_field_template'] = self.list_custom_field_template

        # Add custom field template for table
        if self.table_custom_field_template is not None:
            option['table_custom_field_template'] = self.table_custom_field_template

        if self.table_custom_field_header_template is not None:
            option['table_custom_field_header_template'] = self.table_custom_field_header_template
        
        return option
    