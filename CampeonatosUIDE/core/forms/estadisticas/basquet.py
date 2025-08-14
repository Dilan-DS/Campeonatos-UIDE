from django import forms
from core.models import EstadisticaJugadorBasquet

class EstadisticaJugadorBasquetForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorBasquet
        fields = '__all__'
        widgets = {
            'jugador': forms.Select(attrs={'class': 'select'}),
            'partidos_jugados': forms.NumberInput(attrs={'class': 'input'}),
            'puntos': forms.NumberInput(attrs={'class': 'input'}),
            'asistencias': forms.NumberInput(attrs={'class': 'input'}),
            'rebotes': forms.NumberInput(attrs={'class': 'input'}),
            'robos': forms.NumberInput(attrs={'class': 'input'}),
            'bloqueos': forms.NumberInput(attrs={'class': 'input'}),
        }
