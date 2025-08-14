from django import forms
from core.models import EstadisticaJugadorVideojuegos

class EstadisticaJugadorVideojuegosForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorVideojuegos
        fields = '__all__'
        widgets = {
            'jugador': forms.Select(attrs={'class': 'select'}),
            'partidas_jugadas': forms.NumberInput(attrs={'class': 'input'}),
            'victorias': forms.NumberInput(attrs={'class': 'input'}),
            'derrotas': forms.NumberInput(attrs={'class': 'input'}),
            'kills': forms.NumberInput(attrs={'class': 'input'}),
            'deaths': forms.NumberInput(attrs={'class': 'input'}),
            'asistencias': forms.NumberInput(attrs={'class': 'input'}),
        }