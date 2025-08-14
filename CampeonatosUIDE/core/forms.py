# from django import forms
# from django.core.exceptions import ValidationError
# from django.utils.safestring import mark_safe
# from django.contrib.auth.forms import UserCreationForm
# from .models import *

# class CarreraForm(forms.ModelForm):
#     class Meta:
#         model = Carrera
#         fields = '__all__'
#         widgets = {
#             'nombre': forms.TextInput(attrs={
#                 'placeholder': 'Nombre de la carrera',
#                 'class': 'input'
#             }),
#         }



# class DeporteForm(forms.ModelForm): 
#     class Meta:
#         model = Deporte
#         fields = '__all__'
#         widgets = {
#             'nombre': forms.TextInput(attrs={
#                 'placeholder': 'Ej: Fútbol, Vóley, Básquet...',
#                 'class': 'input'
#             }),
#             'descripcion': forms.Textarea(attrs={
#                 'placeholder': 'Descripción del deporte (opcional)',
#                 'class': 'textarea',
#                 'rows': 3
#             }),
#         }
# # =============================
# # FORMULARIO: SUSPENSIÓN
# # =============================
# class SuspensionForm(forms.ModelForm):
#     class Meta:
#         model = Suspension
#         fields = ['jugador', 'fecha_inicio', 'fecha_fin', 'motivo']
#         widgets = {
#             'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
#             'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
#             'motivo': forms.Textarea(attrs={'class': 'textarea', 'rows': 3, 'placeholder': 'Describe el motivo de la suspensión'}),
#         }
# # =============================
# # FORMULARIO: PARTIDO
# # =============================
# class PartidoForm(forms.ModelForm):
#     class Meta:
#         model = Partido
#         fields = [
#             'campeonato',
#             'equipo_local',
#             'equipo_visitante',
#             'fecha',
#             'hora',
#             'lugar',
#             'arbitro',
#             'resultado_local',
#             'resultado_visitante',
#             'estado',
#         ]
#         widgets = {
#             'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'equipo_local': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'equipo_visitante': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
#             'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'input'}),
#             'lugar': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Lugar del partido'}),
#             'arbitro': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'resultado_local': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Goles equipo local'}),
#             'resultado_visitante': forms.NumberInput(attrs={'class': 'input', 'placeholder': 'Goles equipo visitante'}),
#             'estado': forms.Select(attrs={'class': 'select is-fullwidth'}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         campeonato = cleaned_data.get('campeonato')
#         equipo_local = cleaned_data.get('equipo_local')
#         equipo_visitante = cleaned_data.get('equipo_visitante')
#         fecha = cleaned_data.get('fecha')
#         hora = cleaned_data.get('hora')
#         lugar = cleaned_data.get('lugar')

#         if not all([campeonato, equipo_local, equipo_visitante, fecha, hora, lugar]):
#             return  # Si algún campo obligatorio falta, no seguir validando aquí

#         # Validar que los equipos sean diferentes
#         if equipo_local == equipo_visitante:
#             raise forms.ValidationError("El equipo local y visitante no pueden ser el mismo.")

#         # Validar que la fecha esté dentro del rango del campeonato
#         if fecha < campeonato.fecha_inicio or fecha > campeonato.fecha_fin:
#             raise forms.ValidationError("La fecha del partido debe estar dentro del rango del campeonato.")

#         # Validar que el día del partido esté permitido en el campeonato
#         dias_semana_map = {
#             'Monday': 'LUNES',
#             'Tuesday': 'MARTES',
#             'Wednesday': 'MIERCOLES',
#             'Thursday': 'JUEVES',
#             'Friday': 'VIERNES',
#             'Saturday': 'SABADO',
#             'Sunday': 'DOMINGO',
#         }
#         dia_semana = fecha.strftime('%A')
#         dia_espanol = dias_semana_map.get(dia_semana)
#         if dia_espanol not in campeonato.dias_partido:
#             raise forms.ValidationError(f"El día del partido ({dia_espanol}) no está permitido en el campeonato.")

#         # Validar conflictos de partidos para equipos
#         conflictos = Partido.objects.filter(
#             campeonato=campeonato,
#             fecha=fecha,
#             hora=hora
#         ).filter(
#             Q(equipo_local=equipo_local) | Q(equipo_visitante=equipo_local) |
#             Q(equipo_local=equipo_visitante) | Q(equipo_visitante=equipo_visitante)
#         )

#         # Excluir si se está editando (instance con pk)
#         if self.instance.pk:
#             conflictos = conflictos.exclude(pk=self.instance.pk)

#         if conflictos.exists():
#             raise forms.ValidationError("Alguno de los equipos ya tiene un partido programado en esta fecha y hora.")

#         # Validar conflictos de lugar
#         conflicto_lugar = Partido.objects.filter(
#             campeonato=campeonato,
#             fecha=fecha,
#             hora=hora,
#             lugar__iexact=lugar
#         )
#         if self.instance.pk:
#             conflicto_lugar = conflicto_lugar.exclude(pk=self.instance.pk)

#         if conflicto_lugar.exists():
#             raise forms.ValidationError("Ya hay un partido programado en este lugar, fecha y hora.")

# # =============================
# # FORMULARIO: EQUIPO
# # =============================
# class EquipoForm(forms.ModelForm):
#     """
#     Formulario para registrar o editar un equipo deportivo
#     """

#     class Meta:
#         model = Equipo
#         fields = '__all__'
#         widgets = {
#             'campeonato': forms.Select(attrs={
#                 'class': 'select is-fullwidth'
#             }),
#             'nombre': forms.TextInput(attrs={
#                 'placeholder': 'Nombre del equipo (máximo 100 caracteres)',
#                 'class': 'input'
#             }),
#             'carrera': forms.Select(attrs={
#                 'class': 'select is-fullwidth'
#             }),
#             'logo': forms.ClearableFileInput(attrs={
#                 'class': 'file-input'
#             }),
#             'aprobado': forms.CheckboxInput(attrs={
#                 'class': 'checkbox'
#             }),
#             'delegado': forms.Select(attrs={
#                 'class': 'select is-fullwidth'
#             }),
#             'genero': forms.Select(attrs={
#                 'class': 'select is-fullwidth'
#             }),
#         }

#     def __init__(self, *args, user=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.user = user

#         # 1) Solo permitir campeonatos con inscripción abierta (excluir EN_CURSO/FINALIZADO)
#         self.fields["campeonato"].queryset = Campeonato.objects.exclude(
#             estado__in=["EN_CURSO", "FINALIZADO"]
#         )

#         # 2) Si es DELEGADO: fijar su usuario como delegado y ocultar el campo
#         if user and getattr(user, "rol", "").upper() == "DELEGADO":
#             self.fields["delegado"].queryset = Usuario.objects.filter(pk=user.pk)
#             self.fields["delegado"].initial = user.pk
#             self.fields["delegado"].widget = forms.HiddenInput()

#     def clean(self):
#         cleaned = super().clean()
#         camp = cleaned.get("campeonato")
#         # Bloqueo duro por estado (además del filtro del queryset)
#         if camp and camp.estado in ("EN_CURSO", "FINALIZADO"):
#             self.add_error("campeonato", "No se pueden inscribir equipos en campeonatos en curso o finalizados.")
#         return cleaned


# # =============================
# # FORMULARIO: PAGO
# # =============================
# class PagoForm(forms.ModelForm):
#     class Meta:
#         model = Pago
#         fields = ['equipo', 'metodo', 'codigo_qr', 'comprobante_pago', 'estado', 'observacion_admin']
#         widgets = {
#             'equipo': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'metodo': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'codigo_qr': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'comprobante_pago': forms.ClearableFileInput(attrs={'class': 'file-input'}),
#             'estado': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'observacion_admin': forms.Textarea(attrs={'class': 'textarea', 'rows': 3, 'placeholder': 'Observaciones del administrador (opcional)'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             if isinstance(field.widget, forms.Textarea):
#                 field.widget.attrs.update({'class': 'textarea'})
#             elif isinstance(field.widget, forms.NumberInput):
#                 field.widget.attrs.update({'class': 'input', 'step': '0.01'})
#             elif isinstance(field.widget, forms.TextInput):
#                 field.widget.attrs.update({'class': 'input'})
#             elif isinstance(field.widget, forms.Select):
#                 field.widget.attrs.update({'class': 'select'})

#         if hasattr(self.instance, 'codigo_qr') and self.instance.codigo_qr and hasattr(self.instance.codigo_qr, 'imagen_qr'):
#             self.fields['codigo_qr_preview'] = forms.CharField(
#                 required=False,
#                 label='Vista previa QR',
#                 widget=forms.Textarea(attrs={
#                     'readonly': 'readonly',
#                     'rows': 6,
#                     'class': 'textarea'
#                 }),
#                 initial=mark_safe(
#                     f"<strong>Banco:</strong> {self.instance.codigo_qr.banco}<br>"
#                     f"<img src='{self.instance.codigo_qr.imagen_qr.url}' width='200' style='border:1px solid #ccc;'/>"
#                 )
#             )

# class PagoDelegadoForm(forms.ModelForm):
#     class Meta:
#         model = Pago
#         fields = ['metodo', 'codigo_qr', 'comprobante_pago']
#         widgets = {
#             'metodo': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'codigo_qr': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'comprobante_pago': forms.ClearableFileInput(attrs={'class': 'file-input'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field_name, field in self.fields.items():
#             if isinstance(field.widget, forms.Textarea):
#                 field.widget.attrs.update({'class': 'textarea'})
#             elif isinstance(field.widget, forms.NumberInput):
#                 field.widget.attrs.update({'class': 'input', 'step': '0.01'})
#             elif isinstance(field.widget, forms.TextInput):
#                 field.widget.attrs.update({'class': 'input'})
#             elif isinstance(field.widget, forms.Select):
#                 field.widget.attrs.update({'class': 'select'})

#         if hasattr(self.instance, 'codigo_qr') and self.instance.codigo_qr and hasattr(self.instance.codigo_qr, 'imagen_qr'):
#             self.fields['codigo_qr_preview'] = forms.CharField(
#                 required=False,
#                 label='Vista previa QR',
#                 widget=forms.Textarea(attrs={
#                     'readonly': 'readonly',
#                     'rows': 6,
#                     'class': 'textarea'
#                 }),
#                 initial=mark_safe(
#                     f"<strong>Banco:</strong> {self.instance.codigo_qr.banco}<br>"
#                     f"<img src='{self.instance.codigo_qr.imagen_qr.url}' width='200' style='border:1px solid #ccc;'/>"
#                 )
#             )

#     def clean(self):
#         cleaned_data = super().clean()
#         metodo = cleaned_data.get('metodo')
#         codigo_qr = cleaned_data.get('codigo_qr')
#         comprobante = cleaned_data.get('comprobante_pago')
#         estado = cleaned_data.get('estado')

#         if metodo == 'TRANSFERENCIA' and not codigo_qr:
#             self.add_error('codigo_qr', "Debe seleccionar el banco para transferencia.")

#         if estado in ['APROBADO', 'RECHAZADO'] and not comprobante:
#             self.add_error('comprobante_pago', "Debe subir el comprobante de pago cuando el pago está aprobado o rechazado.")





# # =============================
# # FORMULARIO: CAMPEONATO
# # =============================
# class CampeonatoForm(forms.ModelForm):
#     class Meta:
#         model = Campeonato
#         fields = [
#             'nombre', 
#             'deporte', 
#             'tipo_campeonato', 
#             'descripcion', 
#             'fecha_inicio', 
#             'fecha_fin', 
#             'fecha_fin_inscripcion',
#             'dias_partido', 
#             'max_jugadores_por_equipo', 
#             'reglamento', 
#             'precio_inscripcion', 
#             'codigo_qr', 
#             'delegado', 
#             'estado', 
#             'es_publico', 
#             'activo'
#         ]
#         widgets = {
#             'reglamento': forms.ClearableFileInput(attrs={'class': 'file-input'}),
#             'nombre': forms.TextInput(attrs={
#                 'placeholder': 'Nombre único del campeonato',
#                 'class': 'input'
#             }),
#             'tipo_campeonato': forms.Select(choices=Campeonato.TIPO_CAMPEONATO_CHOICES, attrs={
#                 'class': 'select is-fullwidth'
#             }),
#             'descripcion': forms.Textarea(attrs={
#                 'placeholder': 'Descripción del campeonato (categoría, reglas generales...)',
#                 'class': 'textarea',
#                 'rows': 4
#             }),
            
#             'fecha_inicio': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'input'
#             }),
#             'fecha_fin': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'input'
#             }),
#             'fecha_fin_inscripcion': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'input'
#             }),
#             'estado': forms.Select(attrs={
#                 'class': 'select is-fullwidth'
#             }),
#             'deporte': forms.Select(attrs={
#                 'class': 'select is-fullwidth'
#             }),
#             'delegado': forms.Select(attrs={
#                 'class': 'select is-fullwidth'
#             }),
#             'max_jugadores_por_equipo': forms.NumberInput(attrs={
#                 'placeholder': 'Ej: 7, 11, 5 (según el tipo de campeonato)',
#                 'class': 'input'
#             }),
#             'precio_inscripcion': forms.NumberInput(attrs={
#                 'placeholder': 'Precio de inscripción por equipo',
#                 'class': 'input'
#             }),
#             'codigo_qr': forms.Select(attrs={
#                 'class': 'select is-fullwidth'
#             }),
#             'activo': forms.Select(attrs={'class': 'input is-rounded has-background-light'}),
#             'es_publico': forms.Select(attrs={'class': 'input is-rounded has-background-light'}),

#             'dias_partido': forms.CheckboxSelectMultiple(attrs={
#                 'class': 'checkbox'
#             }),

#         }


# # =============================
# # FORMULARIO: TRANSMISIÓN
# # =============================

# class TransmisionForm(forms.ModelForm):
#     class Meta:
#         model = Transmision
#         fields = ['campeonato', 'partido', 'enlace', 'descripcion', 'activa']
#         widgets = {
#             'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'partido': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'enlace': forms.URLInput(attrs={'class': 'input', 'placeholder': 'URL de la transmisión en vivo'}),
#             'descripcion': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Descripción (opcional)', 'maxlength': 500}),
#             'activa': forms.CheckboxInput(attrs={'class': 'checkbox'}),
#         }

#     def clean_enlace(self):
#         enlace = self.cleaned_data.get('enlace')
#         if not enlace:
#             raise forms.ValidationError("El enlace de la transmisión no puede estar vacío.")
#         return enlace

#     def clean_descripcion(self):
#         descripcion = self.cleaned_data.get('descripcion')
#         if descripcion and len(descripcion) > 500:
#             raise forms.ValidationError("La descripción no puede exceder los 500 caracteres.")
#         return descripcion

# # =============================
# # FORMULARIO DE REGISTRO PÚBLICO — Jugadores y Delegados
# # =============================
# class RegistroUsuarioForm(UserCreationForm):
#     ROL_CHOICES = [
#         ('JUGADOR', 'Jugador'),
#         ('DELEGADO', 'Delegado'),
#     ]
#     rol = forms.ChoiceField(label='Rol', choices=ROL_CHOICES, widget=forms.RadioSelect)
#     cedula = forms.CharField(
#         required=True,
#         max_length=10,
#         label="Cédula",
#         help_text="10 dígitos."
#     )

#     class Meta:
#         model = Usuario
#         fields = (
#             'username', 'first_name', 'last_name', 'email', 'cedula',
#             'carrera', 'genero', 'rol',
#             'password1', 'password2',   # <- asegúrate de incluirlas
#         )
#         labels = {
#             'username':   'Nombre de usuario',
#             'first_name': 'Nombres',
#             'last_name':  'Apellidos',
#             'email':      'Correo electrónico',
#             'carrera':    'Carrera',
#             'genero':     'Género',
#             'rol':        'Rol',
#             'password1':  'Contraseña',
#             'password2':  'Confirmar contraseña',
#         }
#         help_texts = {
#             'username':  'Solo letras, números y @/./+/-/_.',
#             'password1': 'Mínimo 8 caracteres. No totalmente numérica ni muy común.',
#             'password2': 'Repite la contraseña exactamente igual.',
#         }
#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'input',  'placeholder': 'Ej. jlopez'}),
#             'first_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tu nombre'}),
#             'last_name':  forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tus apellidos'}),
#             'email':      forms.EmailInput(attrs={'class': 'input', 'placeholder': 'tucorreo@ejemplo.com'}),
#             # En Bulma, el select suele ir envuelto en <div class="select">, pero dejamos la clase aquí.
#             'carrera': forms.Select(attrs={'class': 'select'}),
#             'genero':  forms.Select(attrs={'class': 'select'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Email obligatorio
#         self.fields['email'].required = True

#         # Estilo de Bulma para contraseñas + ayudas en español
#         self.fields['password1'].widget.attrs.update({'class': 'input'})
#         self.fields['password2'].widget.attrs.update({'class': 'input'})
#         self.fields['password1'].help_text = (
#             "• Mínimo 8 caracteres.<br>"
#             "• No uses algo muy común.<br>"
#             "• No puede ser completamente numérica."
#         )
#         self.fields['password2'].help_text = "Repite la contraseña exactamente igual."

#     def clean_cedula(self):
#         ced = (self.cleaned_data.get("cedula") or "").strip()
#         if not ced.isdigit() or len(ced) != 10:
#             raise ValidationError("La cédula debe tener exactamente 10 dígitos.")
#         # Única (en BD ya es unique, pero validamos antes)
#         if Usuario.objects.filter(cedula__iexact=ced).exists():
#             raise ValidationError("Esta cédula ya está registrada.")
#         return ced

#     def clean_email(self):
#         email = (self.cleaned_data.get('email') or '').strip().lower()
#         if Usuario.objects.filter(email__iexact=email).exists():
#             raise forms.ValidationError('Este correo ya está registrado.')
#         return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.rol = self.cleaned_data.get('rol')
#         # normaliza el correo
#         user.email = (self.cleaned_data.get('email') or '').lower()
#         user.cedula = self.cleaned_data["cedula"].strip()
#         if commit:
#             user.save()
#         return user
# # =============================
# # FORMULARIO: ADMIN CREA USUARIOS (con rol)
# # =============================
# class CrearUsuarioAdminForm(UserCreationForm):
#     class Meta:
#         model = Usuario
#         fields = (
#             'username',
#             'first_name',
#             'last_name',
#             'email',
#             'rol',
#             'carrera',
#             'genero',
#             'password',
#             'password2',
#         )

#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'input'}),
#             'first_name': forms.TextInput(attrs={'class': 'input'}),
#             'last_name': forms.TextInput(attrs={'class': 'input'}),
#             'email': forms.EmailInput(attrs={'class': 'input'}),
#             'rol': forms.Select(attrs={'class': 'select'}),
#             'carrera': forms.TextInput(attrs={'class': 'input'}),
#             'genero': forms.Select(attrs={'class': 'select'}),
#         }

# class CrearUsuarioDelegadoForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)

#     class Meta:
#         model = Usuario
#         fields = ['username', 'first_name', 'last_name', 'email', 'carrera', 'password']
#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'input'}),
#             'first_name': forms.TextInput(attrs={'class': 'input'}),
#             'last_name': forms.TextInput(attrs={'class': 'input'}),
#             'email': forms.EmailInput(attrs={'class': 'input'}),
#             'carrera': forms.Select(attrs={'class': 'select'}),
#             'password': forms.PasswordInput(attrs={'class': 'input'}),
#         }

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         user.rol = 'DELEGADO'
#         if commit:
#             user.save()
#         return user

# class ArbitroForm(forms.ModelForm):
#     username = forms.CharField(max_length=150, required=True, label="Nombre de Usuario")
#     first_name = forms.CharField(max_length=30, required=False, label="Nombres")
#     last_name = forms.CharField(max_length=150, required=False, label="Apellidos")
#     email = forms.EmailField(required=True, label="Correo Electrónico")
#     estado = forms.ChoiceField(
#         choices=[(True, 'Activo'), (False, 'Inactivo')],
#         widget=forms.Select(attrs={'class': 'select is-fullwidth'})
#     )

#     class Meta:
#         model = Arbitro
#         fields = ['username', 'first_name', 'last_name', 'email', 'experiencia', 'deportes', 'contacto', 'estado']
#         widgets = {
#             'experiencia': forms.Textarea(attrs={'class': 'textarea', 'rows': 3, 'placeholder': 'Resumen de experiencia (años, torneos, etc.)'}),
#             'deportes': forms.CheckboxSelectMultiple(),
#             'contacto': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Número de teléfono o email de contacto'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self.instance and self.instance.usuario:
#             self.fields['username'].initial = self.instance.usuario.username
#             self.fields['first_name'].initial = self.instance.usuario.first_name
#             self.fields['last_name'].initial = self.instance.usuario.last_name
#             self.fields['email'].initial = self.instance.usuario.email

#     def save(self, commit=True):
#         arbitro = super().save(commit=False)
#         user = arbitro.usuario
#         user.username = self.cleaned_data['username']
#         user.first_name = self.cleaned_data['first_name']
#         user.last_name = self.cleaned_data['last_name']
#         user.email = self.cleaned_data['email']
#         if commit:
#             user.save()
#             arbitro.save()
#             self.save_m2m() # Save ManyToMany relationships (like 'deportes')
#         return arbitro


# class CrearUsuarioArbitroForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)
#     experiencia = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea', 'rows': 3, 'placeholder': 'Resumen de experiencia (años, torneos, etc.)'}))
#     deportes = forms.ModelMultipleChoiceField(queryset=Deporte.objects.all(), widget=forms.CheckboxSelectMultiple)
#     contacto = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Número de teléfono o email de contacto'}))
#     estado = forms.ChoiceField(
#         choices=[(True, 'Activo'), (False, 'Inactivo')],
#         widget=forms.Select(attrs={'class': 'select is-fullwidth'})
#     )

#     class Meta:
#         model = Usuario
#         fields = ['username', 'first_name', 'last_name', 'email', 'password']
#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'input'}),
#             'first_name': forms.TextInput(attrs={'class': 'input'}),
#             'last_name': forms.TextInput(attrs={'class': 'input'}),
#             'email': forms.EmailInput(attrs={'class': 'input'}),
#             'password': forms.PasswordInput(attrs={'class': 'input'}),
#         }

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         user.rol = 'ARBITRO'
#         if commit:
#             user.save()
#             arbitro = Arbitro.objects.create(
#                 usuario=user,
#                 experiencia=self.cleaned_data['experiencia'],
#                 contacto=self.cleaned_data['contacto'],
#                 estado=self.cleaned_data['estado']
#             )
#             arbitro.deportes.set(self.cleaned_data['deportes'])
#         return user

# class CodigoQRForm(forms.ModelForm):
#     """
#     Formulario para registrar o editar un código QR de banco o método de pago
#     """

#     class Meta:
#         model = CodigoQR
#         fields = [
#             "banco",
#             "descripcion",
#             "imagen_qr",
#             "titular",
#             "identificacion",
#             "tipo_cuenta",
#             "numero_cuenta",
#         ]
#         labels = {
#             "banco": "Nombre del banco",
#             "descripcion": "Descripción adicional",
#             "imagen_qr": "Imagen del QR",
#             "titular": "Titular",
#             "identificacion": "Identificación",
#             "tipo_cuenta": "Tipo de cuenta",
#             "numero_cuenta": "N° de cuenta",
#         }
#         widgets = {
#             "banco": forms.TextInput(attrs={"class": "input", "placeholder": "Banco de Loja"}),
#             "descripcion": forms.Textarea(attrs={"class": "textarea", "rows": 3, "placeholder": "Detalles del QR (opcional)"}),
#             "titular": forms.TextInput(attrs={"class": "input", "placeholder": "Nombre completo del titular"}),
#             "identificacion": forms.TextInput(attrs={"class": "input", "placeholder": "Cédula/RUC (opcional)"}),
#             "tipo_cuenta": forms.Select(),
#             "numero_cuenta": forms.TextInput(attrs={"class": "input", "placeholder": "Ej: 29049255541"}),
#             "imagen_qr": forms.ClearableFileInput(attrs={"class": "file-input", "accept": "image/*"}),
#         }

#     def clean_numero_cuenta(self):
#         nc = self.cleaned_data.get("numero_cuenta", "").strip()
#         if nc and not nc.isdigit():
#             raise forms.ValidationError("El número de cuenta debe contener solo dígitos.")
#         if nc and len(nc) < 6:
#             raise forms.ValidationError("El número de cuenta es demasiado corto.")
#         return nc

# class UsuarioForm(forms.ModelForm):
#     class Meta:
#         model = Usuario
#         fields = ['username', 'email', 'cedula', 'rol']
#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'input'}),
#             'email': forms.EmailInput(attrs={'class': 'input'}),
#             'cedula': forms.TextInput(attrs={'class': 'input'}),
#             'rol': forms.Select(attrs={'class': 'input'}),
#         }

# ##################################
# #jugador
# ##################################
# class JugadorForm(forms.ModelForm):
#     """
#     Formulario para que el jugador complete su perfil inicial.
#     """
#     posicion = forms.CharField(max_length=50, required=False, help_text="Posición principal en el campo (ej: Delantero, Defensa)")

#     class Meta:
#         model = Jugador
#         fields = ['numero_camiseta', 'edad', 'posicion']
#         widgets = {
#             'numero_camiseta': forms.NumberInput(attrs={
#                 'class': 'input',
#                 'placeholder': 'Número de camiseta'
#             }),
#             'edad': forms.NumberInput(attrs={
#                 'class': 'input',
#                 'placeholder': 'Tu edad'
#             }),
#             'posicion': forms.TextInput(attrs={
#                 'class': 'input',
#                 'placeholder': 'Ej: Delantero, Defensa, Portero'
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Asegurarse de que los campos sean requeridos para el jugador
#         self.fields['numero_camiseta'].required = True
#         self.fields['edad'].required = True
#         self.fields['posicion'].required = True


# class EstadisticaJugadorFutbolForm(forms.ModelForm):
#     class Meta:
#         model = EstadisticaJugadorFutbol
#         fields = '__all__'
#         widgets = {
#             'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'partidos_jugados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'goles': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'tarjetas_amarillas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'tarjetas_rojas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#         }

# class EstadisticaJugadorBasquetForm(forms.ModelForm):
#     class Meta:
#         model = EstadisticaJugadorBasquet
#         fields = '__all__'
#         widgets = {
#             'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'partidos_jugados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'canastas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'rebotes': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'asistencias': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#         }

# class EstadisticaJugadorAjedrezForm(forms.ModelForm):
#     class Meta:
#         model = EstadisticaJugadorAjedrez
#         fields = '__all__'
#         widgets = {
#             'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'partidas_jugadas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'partidas_ganadas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'partidas_empatadas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'partidas_perdidas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#         }

# class EstadisticaJugadorEcuabolyForm(forms.ModelForm):
#     class Meta:
#         model = EstadisticaJugadorEcuaboly
#         fields = '__all__'
#         widgets = {
#             'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'partidos_jugados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'sets_ganados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'sets_perdidos': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#         }

# class EstadisticaJugadorPingPongForm(forms.ModelForm):
#     class Meta:
#         model = EstadisticaJugadorPingPong
#         fields = '__all__'
#         widgets = {
#             'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'partidos_jugados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'partidos_ganados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'partidos_perdidos': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#         }

# class EstadisticaJugadorTenisForm(forms.ModelForm):
#     class Meta:
#         model = EstadisticaJugadorTenis
#         fields = '__all__'
#         widgets = {
#             'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'partidos_jugados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'sets_ganados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'sets_perdidos': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#         }

# class EstadisticaJugadorVideojuegosForm(forms.ModelForm):
#     class Meta:
#         model = EstadisticaJugadorVideojuegos
#         fields = '__all__'
#         widgets = {
#             'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'partidas_jugadas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'partidas_ganadas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'partidas_perdidas': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#         }

# class EstadisticaJugadorFutbolinForm(forms.ModelForm):
#     class Meta:
#         model = EstadisticaJugadorFutbolin
#         fields = '__all__'
#         widgets = {
#             'campeonato': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'jugador': forms.Select(attrs={'class': 'select is-fullwidth'}),
#             'partidos_jugados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'partidos_ganados': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'partidos_perdidos': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#             'goles': forms.NumberInput(attrs={'class': 'input', 'min': 0}),
#         }



# class ImagenGaleriaForm(forms.ModelForm):
#     class Meta:
#         model = ImagenGaleria
#         fields = '__all__'
#         widgets = {
#             'titulo': forms.TextInput(attrs={
#                 'class': 'input',
#                 'placeholder': 'Título de la imagen'
#             }),
#             'imagen': forms.ClearableFileInput(attrs={
#                 'class': 'file-input'
#             }),
#             'descripcion': forms.Textarea(attrs={
#                 'class': 'textarea',
#                 'placeholder': 'Descripción opcional',
#                 'rows': 3
#             }),
#             # fecha se auto genera, no va en el form
#         }

# class NoticiaForm(forms.ModelForm):
#     class Meta:
#         model = Noticia
#         fields = '__all__'
#         widgets = {
#             'titulo': forms.TextInput(attrs={
#                 'class': 'input',
#                 'placeholder': 'Título de la noticia'
#             }),
#             'contenido': forms.Textarea(attrs={
#                 'class': 'textarea',
#                 'placeholder': 'Contenido completo de la noticia',
#                 'rows': 5
#             }),
#             'imagen': forms.ClearableFileInput(attrs={
#                 'class': 'file-input'
#             }),
#             # fecha_publicacion es auto, no en form
#         }

# class TestimonioForm(forms.ModelForm):
#     class Meta:
#         model = Testimonio
#         fields = '__all__'
#         widgets = {
#             'autor': forms.TextInput(attrs={
#                 'class': 'input',
#                 'placeholder': 'Nombre del autor del testimonio'
#             }),
#             'contenido': forms.Textarea(attrs={
#                 'class': 'textarea',
#                 'placeholder': 'Contenido del testimonio',
#                 'rows': 4
#             }),
#             'foto': forms.ClearableFileInput(attrs={
#                 'class': 'file-input'
#             }),
#             # fecha auto generado
#         }

# from django.contrib.auth.forms import PasswordResetForm
# from django.contrib.auth import get_user_model

# class PasswordResetConValidacionForm(PasswordResetForm):
#     def clean_email(self):
#         email = self.cleaned_data['email'].strip().lower()
#         U = get_user_model()
#         if not U.objects.filter(email__iexact=email, is_active=True).exists():
#             raise forms.ValidationError("No existe una cuenta activa con ese correo.")
#         return email

# class PerfilUsuarioForm(forms.ModelForm):
#     cedula = forms.CharField(required=True, max_length=10, label="Cédula")
#     class Meta:
#         model = Usuario
#         fields = ["first_name", "last_name", "email", "cedula", "carrera", "genero"]

#     def clean_cedula(self):
#         ced = (self.cleaned_data.get("cedula") or "").strip()
#         if not ced.isdigit() or len(ced) != 10:
#             raise ValidationError("La cédula debe tener exactamente 10 dígitos.")
#         # Única, excluyendo al propio usuario en edición
#         qs = Usuario.objects.filter(cedula__iexact=ced).exclude(pk=self.instance.pk)
#         if qs.exists():
#             raise ValidationError("Esta cédula ya está registrada.")
#         return ced

#     def clean_email(self):
#         email = self.cleaned_data["email"].strip().lower()
#         qs = Usuario.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
#         if qs.exists():
#             raise ValidationError("Ese correo ya está en uso.")
#         return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = (user.email or "").lower()
#         if commit:
#             user.save()
#         return user

# # --- ACTA ÁRBITRO ---
# class ArbitroActaForm(forms.Form):
#     resultado_local = forms.IntegerField(min_value=0, required=True, label="Goles local")
#     resultado_visitante = forms.IntegerField(min_value=0, required=True, label="Goles visitante")
#     tarjetas_amarillas_local = forms.IntegerField(min_value=0, required=False, initial=0)
#     tarjetas_amarillas_visitante = forms.IntegerField(min_value=0, required=False, initial=0)
#     tarjetas_rojas_local = forms.IntegerField(min_value=0, required=False, initial=0)
#     tarjetas_rojas_visitante = forms.IntegerField(min_value=0, required=False, initial=0)
#     observaciones = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows":4}))

#     """
#     Construye campos por jugador:
#     - goles_{jugador_id}  (int >= 0)
#     - amarillas_{jugador_id} (0..2)
#     - roja_{jugador_id}   (0/1)
#     """
#     def __init__(self, *args, jugadores_local=None, jugadores_visitante=None, **kwargs):
#         super().__init__(*args, **kwargs)

#         def add_player_fields(prefix, qs):
#             if qs is None:
#                 return
#             for j in qs:
#                 self.fields[f"goles_{j.id}"] = forms.IntegerField(min_value=0, required=False, initial=0, label=f"Goles {j.usuario.username}")
#                 self.fields[f"amarillas_{j.id}"] = forms.IntegerField(min_value=0, max_value=2, required=False, initial=0, label=f"Amarillas {j.usuario.username}")
#                 self.fields[f"roja_{j.id}"] = forms.IntegerField(min_value=0, max_value=1, required=False, initial=0, label=f"Roja {j.usuario.username}")
#                 self.fields[f"susp_{j.id}"] = forms.BooleanField(required=False, label=f"Suspender {j.usuario.username}")
#                 self.fields[f"susp_ini_{j.id}"] = forms.DateField(required=False, widget=forms.DateInput(attrs={"type":"date"}), label="Desde")
#                 self.fields[f"susp_fin_{j.id}"] = forms.DateField(required=False, widget=forms.DateInput(attrs={"type":"date"}), label="Hasta")
#                 self.fields[f"susp_mot_{j.id}"] = forms.CharField(required=False, max_length=255, label="Motivo")

#         add_player_fields("L", jugadores_local)
#         add_player_fields("V", jugadores_visitante)

#     def total_goles_por_equipo(self, jugadores):
#         total = 0
#         for j in jugadores:
#             total += int(self.cleaned_data.get(f"goles_{j.id}", 0) or 0)
#         return total
