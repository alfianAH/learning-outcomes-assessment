from django.forms import ValidationError


def validate_excel_file(value):
    if not value.name.endswith('.xlsx'):
        raise ValidationError('File harus dalam format Excel (.xlsx, .xls).')

def validate_pdf_file(value):
    if not value.name.endswith('.pdf'):
        raise ValidationError('File harus dalam format PDF (.pdf).')
