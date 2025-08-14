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
            'deportes': forms.SelectMultiple(attrs={'class': 'select is-multiple'}),
            'reglas': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Reglas del campeonato'}),
            'premios': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Premios del campeonato'}),
            'estado': forms.Select(attrs={'class': 'select'}),
            'tipo_campeonato': forms.Select(attrs={'class': 'select'}),
            'modalidad': forms.Select(attrs={'class': 'select'}),
            'max_equipos': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Máximo de equipos'}),
            'min_equipos': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Mínimo de equipos'}),
            'fecha_limite_inscripcion': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'costo_inscripcion': forms.NumberInput(attrs={'class': 'input', 'step': '0.01', 'placeholder': 'Costo de inscripción'}),
            'organizador': forms.Select(attrs={'class': 'select'}),
            'imagen_principal': forms.ClearableFileInput(attrs={'class': 'file-input'}),
        }
