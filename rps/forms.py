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

