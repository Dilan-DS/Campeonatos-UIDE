from django import forms
from core.models import Carrera

class CarreraForm(forms.ModelForm):
    class Meta:
        model = Carrera
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre de la carrera'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'campeonato': forms.Select(attrs={'class': 'select'}),
        }
