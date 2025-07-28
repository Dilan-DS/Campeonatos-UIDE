from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import UserCreationForm
from .models import *

class TipoCampeonatoForm(forms.ModelForm):
    """
    Formulario para registrar o editar un tipo de campeonato
    """

    class Meta:
        model = TipoCampeonato
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ej: Eliminatorias, Fase de Grupos, Torneo Rápido...',
                'class': 'input'
            }),
            'descripcion': forms.Textarea(attrs={
                'placeholder': 'Descripción opcional del tipo de campeonato',
                'class': 'textarea',
                'rows': 3
            }),
        }

class DeporteForm(forms.ModelForm):
    """
    Formulario para registrar o editar un deporte
    """

    class Meta:
        model = Deporte
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ej: Fútbol, Vóley, Básquet...',
                'class': 'input'
            }),
            'descripcion': forms.Textarea(attrs={
                'placeholder': 'Descripción del deporte (opcional)',
                'class': 'textarea',
                'rows': 3
            }),
        }
# =============================
# FORMULARIO: SUSPENSIÓN
# =============================
class SuspensionForm(forms.ModelForm):
    class Meta:
        model = Suspension
        fields = ['jugador', 'fecha_inicio', 'fecha_fin', 'motivo']
        widgets = {
            'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
            'motivo': forms.Textarea(attrs={'class': 'textarea', 'rows': 3, 'placeholder': 'Describe el motivo de la suspensión'}),
        }
# =============================
# FORMULARIO: PARTIDO
# =============================
class PartidoForm(forms.ModelForm):
    class Meta:
        model = Partido
        fields = [
            'campeonato',
            'equipo_local',
            'equipo_visitante',
            'fecha',
            'hora',
            'lugar',
            'arbitro',
            'resultado_local',
            'resultado_visitante',
            'estado',
        ]
        widgets = {
            'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'equipo_local': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'equipo_visitante': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
            'lugar': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Lugar del partido'}),
            'arbitro': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'resultado_local': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Goles equipo local'}),
            'resultado_visitante': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Goles equipo visitante'}),
            'estado': forms.Select(attrs={'class': 'select is-fullwidth'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        campeonato = cleaned_data.get('campeonato')
        equipo_local = cleaned_data.get('equipo_local')
        equipo_visitante = cleaned_data.get('equipo_visitante')
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        lugar = cleaned_data.get('lugar')

        if not all([campeonato, equipo_local, equipo_visitante, fecha, hora, lugar]):
            return  # Si algún campo obligatorio falta, no seguir validando aquí

        # Validar que los equipos sean diferentes
        if equipo_local == equipo_visitante:
            raise forms.ValidationError("El equipo local y visitante no pueden ser el mismo.")

        # Validar que la fecha esté dentro del rango del campeonato
        if fecha < campeonato.fecha_inicio or fecha > campeonato.fecha_fin:
            raise forms.ValidationError("La fecha del partido debe estar dentro del rango del campeonato.")

        # Validar que el día del partido esté permitido en el campeonato
        dias_semana_map = {
            'Monday': 'LUNES',
            'Tuesday': 'MARTES',
            'Wednesday': 'MIERCOLES',
            'Thursday': 'JUEVES',
            'Friday': 'VIERNES',
            'Saturday': 'SABADO',
            'Sunday': 'DOMINGO',
        }
        dia_semana = fecha.strftime('%A')
        dia_espanol = dias_semana_map.get(dia_semana)
        if dia_espanol not in campeonato.dias_partido:
            raise forms.ValidationError(f"El día del partido ({dia_espanol}) no está permitido en el campeonato.")

        # Validar conflictos de partidos para equipos
        conflictos = Partido.objects.filter(
            campeonato=campeonato,
            fecha=fecha,
            hora=hora
        ).filter(
            Q(equipo_local=equipo_local) | Q(equipo_visitante=equipo_local) |
            Q(equipo_local=equipo_visitante) | Q(equipo_visitante=equipo_visitante)
        )

        # Excluir si se está editando (instance con pk)
        if self.instance.pk:
            conflictos = conflictos.exclude(pk=self.instance.pk)

        if conflictos.exists():
            raise forms.ValidationError("Alguno de los equipos ya tiene un partido programado en esta fecha y hora.")

        # Validar conflictos de lugar
        conflicto_lugar = Partido.objects.filter(
            campeonato=campeonato,
            fecha=fecha,
            hora=hora,
            lugar__iexact=lugar
        )
        if self.instance.pk:
            conflicto_lugar = conflicto_lugar.exclude(pk=self.instance.pk)

        if conflicto_lugar.exists():
            raise forms.ValidationError("Ya hay un partido programado en este lugar, fecha y hora.")

# =============================
# FORMULARIO: EQUIPO
# =============================
class EquipoForm(forms.ModelForm):
    """
    Formulario para registrar o editar un equipo deportivo
    """

    class Meta:
        model = Equipo
        fields = '__all__'
        widgets = {
            'campeonato': forms.Select(attrs={
                'class': 'select is-fullwidth'
            }),
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Nombre del equipo (máximo 100 caracteres)',
                'class': 'input'
            }),
            'carrera': forms.Select(attrs={
                'class': 'select is-fullwidth'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'file-input'
            }),
            'aprobado': forms.CheckboxInput(attrs={
                'class': 'checkbox'
            }),
            'delegado': forms.Select(attrs={
                'class': 'select is-fullwidth'
            }),
        }

# =============================
# FORMULARIO: PAGO
# =============================
class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago

        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✔ Añadir estilos Bulma a los campos
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'textarea'})
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({'class': 'input', 'step': '0.01'})
            elif isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': 'input'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'select'})

        # ✅ Si el pago tiene código QR, mostrar vista previa
        if hasattr(self.instance, 'codigo_qr') and self.instance.codigo_qr and hasattr(self.instance.codigo_qr, 'imagen_qr'):
            self.fields['codigo_qr_preview'] = forms.CharField(
                required=False,
                label='Vista previa QR',
                widget=forms.Textarea(attrs={
                    'readonly': 'readonly',
                    'rows': 6,
                    'class': 'textarea'
                }),
                initial=mark_safe(
                    f"<strong>Banco:</strong> {self.instance.codigo_qr.banco}<br>"
                    f"<img src='{self.instance.codigo_qr.imagen_qr.url}' width='200' style='border:1px solid #ccc;'/>"
                )
            )

        fields = ['equipo', 'metodo', 'codigo_qr', 'comprobante_pago', 'estado', 'observacion_admin']
        widgets = {
            'equipo': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'metodo': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'codigo_qr': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'comprobante_pago': forms.ClearableFileInput(attrs={'class': 'file-input'}),
            'estado': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'observacion_admin': forms.Textarea(attrs={'class': 'textarea', 'rows': 3, 'placeholder': 'Observaciones del administrador (opcional)'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get('metodo')
        codigo_qr = cleaned_data.get('codigo_qr')
        comprobante = cleaned_data.get('comprobante_pago')
        estado = cleaned_data.get('estado')

        if metodo == 'TRANSFERENCIA' and not codigo_qr:
            self.add_error('codigo_qr', "Debe seleccionar el banco para transferencia.")

        if estado in ['APROBADO', 'RECHAZADO'] and not comprobante:
            self.add_error('comprobante_pago', "Debe subir el comprobante de pago cuando el pago está aprobado o rechazado.")



# =============================
# FORMULARIO: ÁRBITRO
# =============================
class ArbitroForm(forms.ModelForm):
    """
    Formulario para registrar o editar un árbitro
    """

    class Meta:
        model = Arbitro
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Nombres del árbitro',
                'class': 'input'
            }),
            'apellido': forms.TextInput(attrs={
                'placeholder': 'Apellidos del árbitro',
                'class': 'input'
            }),
            'experiencia': forms.Textarea(attrs={
                'placeholder': 'Resumen de experiencia (años, torneos, etc.)',
                'class': 'textarea',
                'rows': 3
            }),
            'contacto': forms.TextInput(attrs={
                'placeholder': 'Número de teléfono o email de contacto',
                'class': 'input'
            }),
            'estado': forms.CheckboxInput(attrs={
                'class': 'checkbox'
            }),
            'deportes': forms.SelectMultiple(attrs={
                'class': 'select is-multiple is-fullwidth'
            }),
        }

# =============================
# FORMULARIO: CAMPEONATO
# =============================
class CampeonatoForm(forms.ModelForm):
    reglamento = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'file-input'})
    )


    
    class Meta:
        model = Campeonato
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Nombre único del campeonato',
                'class': 'input'
            }),
            'tipo_campeonato': forms.Select(attrs={
                'class': 'select is-fullwidth'
            }),
            'descripcion': forms.Textarea(attrs={
                'placeholder': 'Descripción del campeonato (categoría, reglas generales...)',
                'class': 'textarea',
                'rows': 4
            }),
            
            'fecha_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'input'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'input'
            }),
            'estado': forms.Select(attrs={
                'class': 'select is-fullwidth'
            }),
            'deporte': forms.Select(attrs={
                'class': 'select is-fullwidth'
            }),
            'delegado': forms.Select(attrs={
                'class': 'select is-fullwidth'
            }),
            'max_jugadores_por_equipo': forms.NumberInput(attrs={
                'placeholder': 'Ej: 7, 11, 5 (según el tipo de campeonato)',
                'class': 'input'
            }),
            'precio_inscripcion': forms.NumberInput(attrs={
                'placeholder': 'Precio de inscripción por equipo',
                'class': 'input'
            }),
            'codigo_qr': forms.Select(attrs={
                'class': 'select is-fullwidth'
            }),
            'activo': forms.Select(attrs={'class': 'input is-rounded has-background-light'}),
            'es_publico': forms.Select(attrs={'class': 'input is-rounded has-background-light'}),

            'dias_partido': forms.CheckboxSelectMultiple(attrs={
                'class': 'checkbox'
            }),

        }


# =============================
# FORMULARIO: TRANSMISIÓN
# =============================

class TransmisionForm(forms.ModelForm):
    class Meta:
        model = Transmision
        fields = ['campeonato', 'partido', 'enlace', 'descripcion', 'activa']
        widgets = {
            'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'partido': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'enlace': forms.URLInput(attrs={'class': 'input', 'placeholder': 'URL de la transmisión en vivo'}),
            'descripcion': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Descripción (opcional)', 'maxlength': 500}),
            'activa': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }

    def clean_enlace(self):
        enlace = self.cleaned_data.get('enlace')
        if not enlace:
            raise forms.ValidationError("El enlace de la transmisión no puede estar vacío.")
        return enlace

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if descripcion and len(descripcion) > 500:
            raise forms.ValidationError("La descripción no puede exceder los 500 caracteres.")
        return descripcion

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

class CrearUsuarioDelegadoForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

class CodigoQRForm(forms.ModelForm):
    """
    Formulario para registrar o editar un código QR de banco o método de pago
    """

    class Meta:
        model = CodigoQR
        fields = '__all__'
        widgets = {
            'banco': forms.TextInput(attrs={
                'placeholder': 'Nombre del banco o método (Ej: Banco Pichincha)',
                'class': 'input'
            }),
            'imagen_qr': forms.ClearableFileInput(attrs={
                'class': 'file-input'
            }),
            'descripcion': forms.Textarea(attrs={
                'placeholder': 'Detalles adicionales del código QR (opcional)',
                'class': 'textarea',
                'rows': 3
            }),
        }

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'cedula', 'rol']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'cedula': forms.TextInput(attrs={'class': 'input'}),
            'rol': forms.Select(attrs={'class': 'input'}),
        }

##################################
#jugador
##################################
class JugadorForm(forms.ModelForm):
    """
    Formulario para registrar o editar un jugador en un equipo
    """

    class Meta:
        model = Jugador
        fields = '__all__'
        widgets = {
            'equipo': forms.Select(attrs={
                'class': 'select is-fullwidth'
            }),
            'usuario': forms.Select(attrs={
                'class': 'select is-fullwidth'
            }),
            'numero_camiseta': forms.NumberInput(attrs={
                'class': 'input',
                'placeholder': 'Número único dentro del equipo'
            }),
            'edad': forms.NumberInput(attrs={
                'class': 'input',
                'placeholder': 'Edad mínima 17 años'
            }),
        }

class EstadisticaJugadorFutbolForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorFutbol
        fields = '__all__'
        widgets = {
            'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'partidos_jugados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'goles': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'tarjetas_amarillas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'tarjetas_rojas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
        }

class EstadisticaJugadorBasquetForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorBasquet
        fields = '__all__'
        widgets = {
            'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'partidos_jugados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'canastas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'rebotes': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'asistencias': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
        }

class EstadisticaJugadorAjedrezForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorAjedrez
        fields = '__all__'
        widgets = {
            'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'partidas_jugadas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'partidas_ganadas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'partidas_empatadas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'partidas_perdidas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
        }

class EstadisticaJugadorEcuabolyForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorEcuaboly
        fields = '__all__'
        widgets = {
            'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'partidos_jugados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'sets_ganados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'sets_perdidos': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
        }

class EstadisticaJugadorPingPongForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorPingPong
        fields = '__all__'
        widgets = {
            'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'partidos_jugados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'partidos_ganados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'partidos_perdidos': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
        }

class EstadisticaJugadorTenisForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorTenis
        fields = '__all__'
        widgets = {
            'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'partidos_jugados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'sets_ganados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'sets_perdidos': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
        }

class EstadisticaJugadorVideojuegosForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorVideojuegos
        fields = '__all__'
        widgets = {
            'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'partidas_jugadas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'partidas_ganadas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'partidas_perdidas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
        }

class EstadisticaJugadorFutbolinForm(forms.ModelForm):
    class Meta:
        model = EstadisticaJugadorFutbolin
        fields = '__all__'
        widgets = {
            'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
            'partidos_jugados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'partidos_ganados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'partidos_perdidos': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
            'goles': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
        }



class ImagenGaleriaForm(forms.ModelForm):
    class Meta:
        model = ImagenGaleria
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Título de la imagen'
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'file-input'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'textarea',
                'placeholder': 'Descripción opcional',
                'rows': 3
            }),
            # fecha se auto genera, no va en el form
        }

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Título de la noticia'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'textarea',
                'placeholder': 'Contenido completo de la noticia',
                'rows': 5
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'file-input'
            }),
            # fecha_publicacion es auto, no en form
        }

class TestimonioForm(forms.ModelForm):
    class Meta:
        model = Testimonio
        fields = '__all__'
        widgets = {
            'autor': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Nombre del autor del testimonio'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'textarea',
                'placeholder': 'Contenido del testimonio',
                'rows': 4
            }),
            'foto': forms.ClearableFileInput(attrs={
                'class': 'file-input'
            }),
            # fecha auto generado
        }

