from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import UserCreationForm
from .models import *

class TipoCampeonatoForm(forms.ModelForm):
    class Meta:
        # Definimos el modelo y los campos que queremos incluir en el formulario
        model = TipoCampeonato
        # Especificamos los campos que queremos mostrar en el formulario
        fields = ['nombre', 'descripcion']



class DeporteForm(forms.ModelForm):

    class Meta:
        # Definimos el modelo y los campos que queremos incluir en el formulario
        model = Deporte
        # Especificamos los campos que queremos mostrar en el formulario
        fields = ['nombre', 'descripcion']
# =============================
# FORMULARIO: SUSPENSIÓN
# =============================
class SuspensionForm(forms.ModelForm):
    class Meta:
        # Definimos el modelo y los campos que queremos incluir en el formulario
        model = Suspension
        # Especificamos los campos que queremos mostrar en el formulario
        fields = ['jugador', 'fecha_inicio', 'fecha_fin', 'motivo']
        # Definimos los widgets para los campos de fecha y motivo
        widgets = {
            #
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'motivo': forms.Textarea(attrs={'rows': 3}),
        }

# =============================
# FORMULARIO: PARTIDO
# =============================
class PartidoForm(forms.ModelForm):
    class Meta:
        # Definimos el modelo y los campos que queremos incluir en el formulario
        model = Partido
        # Especificamos los campos que queremos mostrar en el formulario
        fields = ['campeonato', 'equipo_local', 'equipo_visitante', 'fecha', 'hora', 'lugar', 'arbitro']
        # Definimos los widgets para los campos de fecha y hora
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
        }

# =============================
# FORMULARIO: EQUIPO
# =============================
class EquipoForm(forms.ModelForm):
    class Meta:
    # Definimos el modelo y los campos que queremos incluir en el formulario
        model = Equipo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        # Inicializamos el formulario
        super().__init__(*args, **kwargs)
        # Si el equipo ya tiene un campeonato asociado y tiene un código QR
        if self.instance.pk and self.instance.campeonato and hasattr(self.instance.campeonato, 'codigo_qr'):
            # Obtenemos el código QR del campeonato
            codigo_qr = self.instance.campeonato.codigo_qr
            # Si el código QR tiene una imagen asociada, añadimos un campo para mostrarlo
            if hasattr(codigo_qr, 'imagen_qr') and codigo_qr.imagen_qr:
                # Añadimos un campo de texto para mostrar la información del código QR
                self.fields['codigo_qr_info'] = forms.CharField(
                    # Este campo no es obligatorio
                    required=False,
                    # Etiqueta del campo
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
        # Definimos el modelo y los campos que queremos incluir en el formulario
        model = Pago
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si el pago tiene un código QR asociado, añadimos un campo para mostrarlo
        if hasattr(self.instance, 'codigo_qr') and self.instance.codigo_qr and hasattr(self.instance.codigo_qr, 'imagen_qr'):
            # Añadimos un campo de texto para mostrar la información del código QR
            self.fields['codigo_qr_preview'] = forms.CharField(
                # Este campo no es obligatorio
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
        # Definimos el modelo y los campos que queremos incluir en el formulario
        model = Arbitro
        fields = '__all__'

# =============================
# FORMULARIO: CAMPEONATO
# =============================

class CampeonatoForm(forms.ModelForm):
    class Meta:
        # Definimos el modelo y los campos que queremos incluir en el formulario
        model = Campeonato
        fields = '__all__'
        widgets = {
            'dias_partido': forms.CheckboxSelectMultiple(),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }


# =============================
# FORMULARIO: TRANSMISIÓN
# =============================
class TransmisionForm(forms.ModelForm):
    class Meta:
        # Definimos el modelo y los campos que queremos incluir en el formulario
        model = Transmision
        fields = '__all__'

# =============================
# FORMULARIO DE REGISTRO PÚBLICO — Solo jugadores
# =============================
class RegistroJugadorForm(UserCreationForm):
    class Meta:
        # Definimos el modelo y los campos que queremos incluir en el formulario
        model = Usuario
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'carrera',
            'password1',
            'password2',
        )

        widgets = {
            'username': forms.TextInput(attrs={'class': 'input'}),
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'carrera': forms.TextInput(attrs={'class': 'input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'JUGADOR'  # Por defecto va jugador
        if commit:
            # Guardamos el usuario en la base de datos
            user.save()
        # Retornamos el usuario creado
        return user

# =============================
# FORMULARIO: ADMIN CREA USUARIOS (con rol)
# =============================
class CrearUsuarioAdminForm(UserCreationForm):
    class Meta:
        model = Usuario
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
