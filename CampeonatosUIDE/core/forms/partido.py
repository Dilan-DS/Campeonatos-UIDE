from django import forms
from core.models import Partido

class PartidoForm(forms.ModelForm):
    class Meta:
        model = Partido
        fields = '__all__'
        widgets = {
            'campeonato': forms.Select(attrs={'class': 'select'}),
            'equipo_local': forms.Select(attrs={'class': 'select'}),
            'equipo_visitante': forms.Select(attrs={'class': 'select'}),
            'fecha': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'input', 'type': 'time'}),
            'lugar': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Lugar del partido'}),
            'arbitro': forms.Select(attrs={'class': 'select'}),
            'estado': forms.Select(attrs={'class': 'select'}),
            'resultado_local': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Resultado local'}),
            'resultado_visitante': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Resultado visitante'}),
        }

class ArbitroActaForm(forms.ModelForm):
    class Meta:
        model = Partido
        fields = ['resultado_local', 'resultado_visitante', 'estado']
        widgets = {
            'resultado_local': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Goles Local'}),
            'resultado_visitante': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Goles Visitante'}),
            'estado': forms.Select(attrs={'class': 'select'}),
        }
