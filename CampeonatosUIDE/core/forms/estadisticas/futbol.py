from django import forms
from core.models import EstadisticaJugadorFutbol

class EstadisticaJugadorFutbolForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorFutbol
        fields = '__all__'
        widgets = {
            'jugador': forms.Select(attrs={'class': 'select'}),
            'partidos_jugados': forms.NumberInput(attrs={'class': 'input'}),
            'goles': forms.NumberInput(attrs={'class': 'input'}),
            'asistencias': forms.NumberInput(attrs={'class': 'input'}),
            'tarjetas_amarillas': forms.NumberInput(attrs={'class': 'input'}),
            'tarjetas_rojas': forms.NumberInput(attrs={'class': 'input'}),
        }
