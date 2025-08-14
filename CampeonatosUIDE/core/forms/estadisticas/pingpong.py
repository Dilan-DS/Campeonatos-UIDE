from django import forms
from core.models import EstadisticaJugadorPingPong

class EstadisticaJugadorPingPongForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorPingPong
        fields = '__all__'
        widgets = {
            'jugador': forms.Select(attrs={'class': 'select'}),
            'partidos_jugados': forms.NumberInput(attrs={'class': 'input'}),
            'victorias': forms.NumberInput(attrs={'class': 'input'}),
            'derrotas': forms.NumberInput(attrs={'class': 'input'}),
            'sets_ganados': forms.NumberInput(attrs={'class': 'input'}),
            'sets_perdidos': forms.NumberInput(attrs={'class': 'input'}),
        }
