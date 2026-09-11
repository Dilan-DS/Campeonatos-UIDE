from django import forms
from core.models import Campeonato

class CampeonatoForm(forms.ModelForm):
    class Meta:
        model = Campeonato
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre del campeonato'}),
            'descripcion': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Descripción del campeonato'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'select'}),
            'tipo_campeonato': forms.Select(attrs={'class': 'select'}),
        }
