from django import forms
from .models import RencanaPembelajaranSemester


class RPSModelForm(forms.ModelForm):
    class Meta:
        model = RencanaPembelajaranSemester
        fields = ['file_rps']
        labels = {
            'file_rps': 'Unggah File RPS'
        }
        widgets = {
            'file_rps': forms.FileInput(attrs={
                'accept': 'application/pdf'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file_rps'].required = False

    def clean(self):
        cleaned_data = super().clean()

        file_rps = cleaned_data.get('file_rps')
        if file_rps is None:
            self.add_error('file_rps', 'File RPS harus diisi.')
        
        return cleaned_data
