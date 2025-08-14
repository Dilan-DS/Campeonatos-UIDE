from django import forms
from core.models import Transmision

class TransmisionForm(forms.ModelForm):
    class Meta:
        model = Transmision
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Título de la transmisión'}),
            'url': forms.URLInput(attrs={'class': 'input', 'placeholder': 'URL de la transmisión'}),
            'fecha_hora': forms.DateTimeInput(attrs={'class': 'input', 'type': 'datetime-local'}),
            'partido': forms.Select(attrs={'class': 'select'}),
        }
