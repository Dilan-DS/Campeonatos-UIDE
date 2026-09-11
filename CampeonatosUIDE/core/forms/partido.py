from django import forms
from django.core.exceptions import ValidationError as DjangoValidationError
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

class ArbitroActaForm(forms.Form):
    """Acta de partido que carga el árbitro.

    Es un Form (no ModelForm): la vista asigna los valores a Partido y guarda
    a mano, además de crear estadísticas y suspensiones por jugador.

    Al migrar los formularios de core/forms.py al paquete core/forms/ esta
    clase quedó como un ModelForm de tres campos, sin el __init__ que crea los
    campos por jugador. Como acta_partido_arbitro la instancia con
    jugadores_local/jugadores_visitante, la carga del acta respondía
    TypeError (HTTP 500) y el árbitro no podía registrar ningún resultado.

    Contrato que espera la vista:
      · resultado_local / resultado_visitante            (obligatorios)
      · tarjetas_amarillas_* / tarjetas_rojas_*          (opcionales)
      · observaciones                                    (opcional)
      · por jugador: goles_<id>, amarillas_<id>, roja_<id>,
        susp_<id>, susp_ini_<id>, susp_fin_<id>, susp_mot_<id>
      · total_goles_por_equipo(jugadores)
    """

    resultado_local = forms.IntegerField(
        min_value=0, required=True, label="Goles local",
        widget=forms.NumberInput(attrs={'class': 'input', 'min': 0}))
    resultado_visitante = forms.IntegerField(
        min_value=0, required=True, label="Goles visitante",
        widget=forms.NumberInput(attrs={'class': 'input', 'min': 0}))
    # Tanda de penaltis: solo se rellena si el partido acaba empatado y es
    # de eliminatoria. Es lo unico que puede decidir quien pasa de ronda.
    penales_local = forms.IntegerField(
        min_value=0, required=False, label="Penaltis local",
        widget=forms.NumberInput(attrs={'class': 'input', 'min': 0}))
    penales_visitante = forms.IntegerField(
        min_value=0, required=False, label="Penaltis visitante",
        widget=forms.NumberInput(attrs={'class': 'input', 'min': 0}))
    tarjetas_amarillas_local = forms.IntegerField(
        min_value=0, required=False, initial=0, label="Amarillas local",
        widget=forms.NumberInput(attrs={'class': 'input', 'min': 0}))
    tarjetas_amarillas_visitante = forms.IntegerField(
        min_value=0, required=False, initial=0, label="Amarillas visitante",
        widget=forms.NumberInput(attrs={'class': 'input', 'min': 0}))
    tarjetas_rojas_local = forms.IntegerField(
        min_value=0, required=False, initial=0, label="Rojas local",
        widget=forms.NumberInput(attrs={'class': 'input', 'min': 0}))
    tarjetas_rojas_visitante = forms.IntegerField(
        min_value=0, required=False, initial=0, label="Rojas visitante",
        widget=forms.NumberInput(attrs={'class': 'input', 'min': 0}))
    observaciones = forms.CharField(
        required=False, label="Observaciones del árbitro",
        widget=forms.Textarea(attrs={'class': 'textarea', 'rows': 4,
                                     'placeholder': 'Incidencias relevantes del partido'}))

    def __init__(self, *args, jugadores_local=None, jugadores_visitante=None, **kwargs):
        super().__init__(*args, **kwargs)
        for qs in (jugadores_local, jugadores_visitante):
            if qs is None:
                continue
            for j in qs:
                nombre = j.usuario.get_full_name() or j.usuario.username
                self.fields[f"goles_{j.id}"] = forms.IntegerField(
                    min_value=0, required=False, initial=0, label=f"Goles {nombre}",
                    widget=forms.NumberInput(attrs={'class': 'input', 'min': 0}))
                self.fields[f"amarillas_{j.id}"] = forms.IntegerField(
                    min_value=0, max_value=2, required=False, initial=0,
                    label=f"Amarillas {nombre}",
                    widget=forms.NumberInput(attrs={'class': 'input', 'min': 0, 'max': 2}))
                self.fields[f"roja_{j.id}"] = forms.IntegerField(
                    min_value=0, max_value=1, required=False, initial=0,
                    label=f"Roja {nombre}",
                    widget=forms.NumberInput(attrs={'class': 'input', 'min': 0, 'max': 1}))
                self.fields[f"susp_{j.id}"] = forms.BooleanField(
                    required=False, label=f"Suspender a {nombre}",
                    widget=forms.CheckboxInput(attrs={'class': 'checkbox'}))
                self.fields[f"susp_ini_{j.id}"] = forms.DateField(
                    required=False, label="Desde",
                    widget=forms.DateInput(attrs={'class': 'input', 'type': 'date'}))
                self.fields[f"susp_fin_{j.id}"] = forms.DateField(
                    required=False, label="Hasta",
                    widget=forms.DateInput(attrs={'class': 'input', 'type': 'date'}))
                self.fields[f"susp_mot_{j.id}"] = forms.CharField(
                    required=False, max_length=255, label="Motivo",
                    widget=forms.TextInput(attrs={'class': 'input',
                                                  'placeholder': 'Motivo de la suspensión'}))


    def clean(self):
        """Comprueba la tanda con las mismas reglas que el modelo.

        Se construye un Partido en memoria y se delega en su clean(), asi
        las reglas viven en un solo sitio: penaltis solo con empate, los dos
        equipos o ninguno, y la tanda no puede quedar igualada.
        """
        limpios = super().clean()

        from core.models import Partido

        provisional = Partido(
            resultado_local=limpios.get("resultado_local"),
            resultado_visitante=limpios.get("resultado_visitante"),
            penales_local=limpios.get("penales_local"),
            penales_visitante=limpios.get("penales_visitante"),
        )
        try:
            provisional.clean()
        except DjangoValidationError as error:
            # El mensaje habla de la tanda, asi que se muestra junto a ella.
            self.add_error("penales_local", error.messages[0])

        return limpios

    def total_goles_por_equipo(self, jugadores):
        """Suma los goles cargados por jugador para validarlos contra el marcador."""
        return sum(int(self.cleaned_data.get(f"goles_{j.id}", 0) or 0) for j in jugadores)
