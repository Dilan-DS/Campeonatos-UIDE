from django import forms
from core.models import Transmision

class TransmisionForm(forms.ModelForm):
    class Meta:
        model = Transmision
        fields = '__all__'
        widgets = {
            'enlace': forms.URLInput(attrs={'class': 'input', 'placeholder': 'URL de la transmisión'}),
            'partido': forms.Select(attrs={'class': 'select'}),
        }
