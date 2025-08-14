from django import forms
from core.models import EstadisticaJugadorAjedrez

class EstadisticaJugadorAjedrezForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorAjedrez
        fields = '__all__'
        widgets = {
            'jugador': forms.Select(attrs={'class': 'select'}),
            'partidas_jugadas': forms.NumberInput(attrs={'class': 'input'}),
            'victorias': forms.NumberInput(attrs={'class': 'input'}),
            'derrotas': forms.NumberInput(attrs={'class': 'input'}),
            'empates': forms.NumberInput(attrs={'class': 'input'}),
            'puntos': forms.NumberInput(attrs={'class': 'input'}),
        }
