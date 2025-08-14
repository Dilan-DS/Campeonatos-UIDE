from django import forms
from core.models import EstadisticaJugadorEcuaboly

class EstadisticaJugadorEcuabolyForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorEcuaboly
        fields = '__all__'
        widgets = {
            'jugador': forms.Select(attrs={'class': 'select'}),
            'partidos_jugados': forms.NumberInput(attrs={'class': 'input'}),
            'puntos_a_favor': forms.NumberInput(attrs={'class': 'input'}),
            'puntos_en_contra': forms.NumberInput(attrs={'class': 'input'}),
            'victorias': forms.NumberInput(attrs={'class': 'input'}),
            'derrotas': forms.NumberInput(attrs={'class': 'input'}),
        }