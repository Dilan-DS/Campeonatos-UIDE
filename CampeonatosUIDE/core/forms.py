from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import UserCreationForm
from .models import Equipo, Pago, Arbitro, Campeonato, Transmision, Usuario, Partido, Suspension

class SuspensionForm(forms.ModelForm):
    class Meta:
        model = Suspension
        fields = ['jugador', 'fecha_inicio', 'fecha_fin', 'motivo']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.Textarea(attrs={'rows': 3}),
        }

class PartidoForm(forms.ModelForm):
    class Meta:
        model = Partido
        fields = ['campeonato', 'equipo_local', 'equipo_visitante', 'fecha', 'hora', 'lugar', 'arbitro']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
        }
# =============================
# FORMULARIO: EQUIPO
# =============================
class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.instance.campeonato and hasattr(self.instance.campeonato, 'codigo_qr'):
            codigo_qr = self.instance.campeonato.codigo_qr
            if hasattr(codigo_qr, 'imagen_qr') and codigo_qr.imagen_qr:
                self.fields['codigo_qr_info'] = forms.CharField(
                    required=False,
                    label="Código QR del campeonato",
                    widget=forms.Textarea(attrs={'readonly': 'readonly', 'rows': 6}),
                    initial=mark_safe(
                        f"<strong>Banco:</strong> {codigo_qr.banco}<br>"
                        f"<img src='{codigo_qr.imagen_qr.url}' width='200' style='border:1px solid #ccc; padding:5px'/>"
                    )
                )


# =============================
# FORMULARIO: PAGO
# =============================
class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(self.instance, 'codigo_qr') and self.instance.codigo_qr and hasattr(self.instance.codigo_qr, 'imagen_qr'):
            self.fields['codigo_qr_preview'] = forms.CharField(
                required=False,
                label='Vista previa QR',
                widget=forms.Textarea(attrs={'readonly': 'readonly', 'rows': 6}),
                initial=mark_safe(
                    f"<strong>Banco:</strong> {self.instance.codigo_qr.banco}<br>"
                    f"<img src='{self.instance.codigo_qr.imagen_qr.url}' width='200' style='border:1px solid #ccc;'/>"
                )
            )


# =============================
# FORMULARIO: ÁRBITRO
# =============================
class ArbitroForm(forms.ModelForm):
    class Meta:
        model = Arbitro
        fields = '__all__'


# =============================
# FORMULARIO: CAMPEONATO
# =============================
class CampeonatoForm(forms.ModelForm):
    class Meta:
        model = Campeonato
        fields = '__all__'


# =============================
# FORMULARIO: TRANSMISIÓN
# =============================
class TransmisionForm(forms.ModelForm):
    class Meta:
        model = Transmision
        fields = '__all__'


# =============================
# FORMULARIO: USUARIO PERSONALIZADO
# =============================
class CustomUsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario  # Tu modelo personalizado
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'rol',
            'carrera',
            'password1',
            'password2',
        )

        widgets = {
            'username': forms.TextInput(attrs={'class': 'input'}),
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'rol': forms.Select(attrs={'class': 'select'}),
            'carrera': forms.TextInput(attrs={'class': 'input'}),
        }