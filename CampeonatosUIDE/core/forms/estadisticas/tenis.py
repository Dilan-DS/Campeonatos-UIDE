from django import forms
from core.models import EstadisticaJugadorTenis

class EstadisticaJugadorTenisForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorTenis
        fields = '__all__'
        widgets = {
            'jugador': forms.Select(attrs={'class': 'select'}),
            'partidos_jugados': forms.NumberInput(attrs={'class': 'input'}),
            'victorias': forms.NumberInput(attrs={'class': 'input'}),
            'derrotas': forms.NumberInput(attrs={'class': 'input'}),
            'sets_ganados': forms.NumberInput(attrs={'class': 'input'}),
            'sets_perdidos': forms.NumberInput(attrs={'class': 'input'}),
            'juegos_ganados': forms.NumberInput(attrs={'class': 'input'}),
            'juegos_perdidos': forms.NumberInput(attrs={'class': 'input'}),
        }