from django import forms
from core.models import Equipo, Jugador

class EquipoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.campeonato = kwargs.pop('campeonato', None)
        self.campeonato_id = kwargs.pop('campeonato_id', None)
        super().__init__(*args, **kwargs)

        if 'campeonato' in self.fields and not self.instance.pk:
            if self.campeonato is not None:
                self.fields['campeonato'].initial = self.campeonato
            elif self.campeonato_id is not None:
                self.fields['campeonato'].initial = self.campeonato_id

    class Meta:
        model = Equipo
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre del equipo'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'file-input'}),
            'campeonato': forms.Select(attrs={'class': 'select'}),
            'delegado': forms.Select(attrs={'class': 'select'}),
        }

class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre del jugador'}),
            'apellido': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Apellido del jugador'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'equipo': forms.Select(attrs={'class': 'select'}),
            'posicion': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Posición del jugador'}),
            'numero_camiseta': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Número de camiseta'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'file-input'}),
        }
