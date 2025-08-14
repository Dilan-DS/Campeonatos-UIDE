from django import forms
from core.models import EstadisticaJugadorFutbolin

class EstadisticaJugadorFutbolinForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorFutbolin
        fields = '__all__'
        widgets = {
            'jugador': forms.Select(attrs={'class': 'select'}),
            'partidas_jugadas': forms.NumberInput(attrs={'class': 'input'}),
            'victorias': forms.NumberInput(attrs={'class': 'input'}),
            'derrotas': forms.NumberInput(attrs={'class': 'input'}),
            'goles_a_favor': forms.NumberInput(attrs={'class': 'input'}),
            'goles_en_contra': forms.NumberInput(attrs={'class': 'input'}),
        }