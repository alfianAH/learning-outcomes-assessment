from django import forms
from django.conf import settings
from django.forms import CheckboxSelectMultiple
from django.forms.widgets import (
    ChoiceWidget,
    Input,
    Select,
    Textarea,
    CheckboxSelectMultiple,
)
from django_filters.widgets import SuffixedMultiWidget


class ChoiceListInteractiveModelA(CheckboxSelectMultiple):
    is_required: bool = False
    input_type: str = 'checkbox'
    template_name: str = 'custom-widgets/forms/widgets/list-item-model-a/checkbox-select-list-item-model-a.html'
    option_template_name: str = 'custom-widgets/forms/widgets/list-item-model-a/checkbox-option-list-item-model-a.html'
    badge_template: str = None
    list_custom_field_template: str = None
    table_custom_field_template: str = None
    table_custom_field_header_template: str = None
    condition_dict: dict = {}

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
        if len(self.condition_dict.items()) != 0:
            for key, value in self.condition_dict.items():
                # check the right value
                if option['value'] != key: continue
                # If value is true, continue
                if value: continue
                # If value is False, make it disabled
                option['attrs']['disabled'] = ''
        
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


class UpdateChoiceList(CheckboxSelectMultiple):
    is_required: bool = False
    input_type: str = 'checkbox'
    template_name: str = 'custom-widgets/forms/widgets/list-item-model-c/checkbox-select-list-item-model-c.html'
    option_template_name: str = 'custom-widgets/forms/widgets/list-item-model-c/checkbox-option-list-item-model-c.html'
    list_item_name: str = 'components/list-table-view/model-c/list-item-name.html'
    badge_template: str = None
    list_custom_field_template: str = None

    def __init__(self, 
        badge_template: str = None, 
        list_custom_field_template: str = None,
        *args, **kwargs):
        if 'list_item_name' in kwargs.keys():
            self.list_item_name = kwargs.pop('list_item_name')
        
        super().__init__(*args, **kwargs)
        self.badge_template = badge_template or None
        self.list_custom_field_template = list_custom_field_template or None

    def create_option(self, *args, **kwargs):
        option = super().create_option(*args, **kwargs)

        # Add badget template
        if self.badge_template is not None:
            option['badge_template'] = self.badge_template
        
        # Add custom field template for list
        if self.list_custom_field_template is not None:
            option['list_custom_field_template'] = self.list_custom_field_template

        # add custom list item name
        if self.list_item_name is not None:
            option['list_item_name'] = self.list_item_name
        
        return option


class MyNumberInput(Input):
    input_type: str = 'number'
    template_name: str = 'custom-widgets/forms/widgets/number.html'


class MyTextInput(Input):
    input_type: str = 'text'
    template_name: str = 'custom-widgets/forms/widgets/text.html'


class MyRangeInput(Input):
    input_type: str = 'number'
    template_name: str = 'custom-widgets/forms/widgets/range-input.html'


class MyRangeWidget(SuffixedMultiWidget):
    template_name: str = 'custom-widgets/forms/widgets/multiwidget.html'
    suffixes = ["min", "max"]

    def __init__(self, widgets, attrs=None):
        super().__init__(widgets, attrs)


class MyTextareaInput(Textarea):
    template_name: str = 'custom-widgets/forms/widgets/textarea.html'


class MySearchInput(Input):
    input_type: str = 'text'
    template_name: str = 'custom-widgets/forms/widgets/search-text-input.html'


class MySelectInput(Select):
    template_name: str = 'custom-widgets/forms/widgets/select.html'


class MyColorSelectInput(Select):
    template_name: str = 'custom-widgets/forms/widgets/color-select.html'
    option_template_name: str = 'custom-widgets/forms/widgets/color-select-option.html'


class MyRadioInput(ChoiceWidget):
    input_type: str = 'radio'
    template_name: str = 'custom-widgets/forms/widgets/radio-input.html'
    option_template_name: str = 'custom-widgets/forms/widgets/radio-option.html'


class MyCheckboxInput(CheckboxSelectMultiple):
    template_name = 'custom-widgets/forms/widgets/checkbox-select.html'
    option_template_name: str = 'custom-widgets/forms/widgets/checkbox-option.html'



class PagedownWidget(forms.Textarea):
    """Pagedown Widget
    Copyright (c) 2019, Timmy O'Mahony
    All rights reserved.
    """
    template_name = 'custom-widgets/forms/widgets/pagedown/default.html'

    def __init__(self, attrs=None):
        super(PagedownWidget, self).__init__(attrs=attrs)
        # Add wmd-input class for easier styling
        self.attrs['class'] = '{} wmd-input'.format(
            self.attrs.get('class', ''))

    def get_context(self, name, value, attrs):
        context = super(PagedownWidget, self).get_context(name, value, attrs)
        context["image_upload_enabled"] = getattr(
            settings, 'PAGEDOWN_IMAGE_UPLOAD_ENABLED', False)
        return context

    class Media:
        css = {
            'all': (
                'public/pagedown/pagedown/demo/browser/demo.css',
                'public/pagedown/pagedown.css'
            )
        }
        js = (
            'public/pagedown/pagedown/Markdown.Converter.js',
            'public/pagedown/pagedown-extra/pagedown/Markdown.Converter.js',
            'public/pagedown/pagedown/Markdown.Sanitizer.js',
            'public/pagedown/pagedown/Markdown.Editor.js',
            'public/pagedown/pagedown-extra/Markdown.Extra.js',
            'public/pagedown/pagedown_init.js'
        )

