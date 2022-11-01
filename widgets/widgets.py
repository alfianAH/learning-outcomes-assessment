from django.forms.widgets import ChoiceWidget

class ChoiceListInteractive(ChoiceWidget):
    input_type = 'checkbox'
    template_name: str = 'custom-widgets/forms/widgets/checkbox_select.html'
    option_template_name: str = 'custom-widgets/forms/widgets/checkbox_option.html'
    badge_template: str = None
    custom_field_template: str = None

    def __init__(self, badge_template: str = ..., custom_field_template: str = ..., *args, **kwargs):
        super().__init__(*args, **kwargs)
        if badge_template is not None:
            self.badge_template = badge_template
        if custom_field_template is not None:
            self.custom_field_template = custom_field_template

    def create_option(self, *args, **kwargs):
        option = super().create_option(*args, **kwargs)
        
        # Add badget template
        if self.badge_template is not None:
            option['badge_template'] = self.badge_template
        
        # Add custom field template
        if self.custom_field_template is not None:
            option['custom_field_template'] = self.custom_field_template
        
        return option
    