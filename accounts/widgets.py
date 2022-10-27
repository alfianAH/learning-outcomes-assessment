from django.forms.widgets import Input
from django.forms.widgets import Select


class LoginTextInput(Input):
    input_type: str = 'text'
    template_name: str = 'custom-widgets/forms/widgets/accounts/text.html'

class LoginPasswordInput(Input):
    input_type: str = 'password'
    template_name: str = 'custom-widgets/forms/widgets/accounts/password.html'

class LoginSelect(Select):
    input_type = 'select'
    template_name = 'custom-widgets/forms/widgets/accounts/select.html'