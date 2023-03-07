from django.forms import ValidationError


def validate_excel_file(value):
    if not value.name.endswith('.xlsx'):
        raise ValidationError('File harus dalam format Excel (.xlsx, .xls).')
