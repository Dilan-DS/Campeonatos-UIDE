from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Q, Sum
from django.utils.functional import cached_property

# Modelos base reutilizables

class TimeStampedModel(models.Model):
    """Modelo base abstracto que añade campos de timestamp auto-actualizables."""
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# Modelo carrera
class Carrera(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

# Modelo personalizado de usuario
class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    EMAIL_FIELD = "email"

    ROLES = [
        ('ADMIN', 'Administrador'),
        ('DELEGADO', 'Delegado de Carrera'),
        ('ARBITRO', 'Árbitro'),
        ('JUGADOR', 'Jugador'),
    ]
    cedula = models.CharField(max_length=10, unique=True, null=True, blank=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='JUGADOR')
    carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, null=True, blank=True)
    groups = models.ManyToManyField(
        Group,
        related_name='usuarios_custom',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
        related_query_name='usuario_custom',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuarios_custom',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
        related_query_name='usuario_custom',
    )
    GENERO_CHOICES = (
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
    )
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.rol})"

# Modelo de deporte
class Deporte(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# Modelo árbitro
class Arbitro(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'ARBITRO'})
    experiencia = models.TextField()
    deportes = models.ManyToManyField(Deporte, related_name='arbitros')
    contacto = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.username} ({self.usuario.get_rol_display()})"

class CodigoQR(models.Model):
    banco = models.CharField(max_length=100, verbose_name="Nombre del banco")
    imagen_qr = models.ImageField(upload_to='codigos_qr/', verbose_name="Imagen del QR")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción adicional")
    TIPO_CUENTA_CHOICES = [('AHORROS','Ahorros'),('CORRIENTE','Corriente')]
    tipo_cuenta = models.CharField(max_length=20, choices=TIPO_CUENTA_CHOICES, default='AHORROS')
    numero_cuenta = models.CharField(max_length=30)
    titular = models.CharField(max_length=150)
    identificacion = models.CharField(max_length=20, blank=True, null=True)
    activo = models.BooleanField(default=True, help_text="Si está activo, se muestra a los delegados.")
    es_principal = models.BooleanField(default=False, help_text="Si está marcado, se usa por defecto.")
    class Meta:
        verbose_name = "Código QR"
        verbose_name_plural = "Códigos QR"
        constraints = [
            models.UniqueConstraint(fields=['banco','numero_cuenta'], name='uniq_banco_numero_cuenta')
        ]
        ordering = ['-es_principal','banco','numero_cuenta']
    def __str__(self):
        return f"{self.banco} - {self.get_tipo_cuenta_display()} - {self.numero_cuenta}"
    def clean(self):
        errors = {}
        if not self.imagen_qr:
            errors['imagen_qr'] = "La imagen del código QR es obligatoria."
        if self.descripcion and len(self.descripcion) > 500:
            errors['descripcion'] = "La descripción no puede exceder los 500 caracteres."
        if errors:
            raise ValidationError(errors)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.es_principal:
            CodigoQR.objects.exclude(pk=self.pk).update(es_principal=False)
    def to_dict(self):
        return {
            "banco": self.banco,
            "tipo_cuenta": self.get_tipo_cuenta_display(),
            "numero_cuenta": self.numero_cuenta,
            "titular": self.titular,
            "identificacion": self.identificacion or "",
            "imagen_qr": self.imagen_qr.url if self.imagen_qr else "",
        }
    @classmethod
    def visibles_para_delegados(cls):
        return cls.objects.filter(activo=True).order_by('-es_principal','banco')

# Modelo campeonato
class Campeonato(models.Model):
    DIAS_SEMANA = [
        ('LUNES', 'Lunes'), ('MARTES', 'Martes'), ('MIERCOLES', 'Miércoles'),
        ('JUEVES', 'Jueves'), ('VIERNES', 'Viernes'), ('SABADO', 'Sábado'), ('DOMINGO', 'Domingo'),
    ]
    ESTADOS = [
        ('INSCRIPCION', 'Inscripción Abierta'), ('CERRADO', 'Inscripción Cerrada'),
        ('EN_CURSO', 'En Curso'), ('FINALIZADO', 'Finalizado'),
    ]
    OPCIONES_SI_NO = [('SI', 'Sí'), ('NO', 'No')]
    TIPO_CAMPEONATO_CHOICES = [
        ('FASE_GRUPOS', 'Fase de Grupos'), ('ELIMINATORIA', 'Eliminatoria Simple'),
        ('LIGA', 'Todos contra todos'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    tipo_campeonato = models.CharField(max_length=20, choices=TIPO_CAMPEONATO_CHOICES)
    descripcion = models.TextField()
    reglamento = models.FileField(upload_to='reglamentos/', blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_fin_inscripcion = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='INSCRIPCION')
    deporte = models.ForeignKey(Deporte, on_delete=models.CASCADE, related_name='campeonatos')
    delegado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, related_name='campeonatos_delegado', blank=True, null=True)
    dias_partido = MultiSelectField(choices=DIAS_SEMANA, blank=True, default=[])
    max_jugadores_por_equipo = models.PositiveIntegerField(default=11, help_text="Cantidad máxima de jugadores por equipo")
    precio_inscripcion = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    codigo_qr = models.ForeignKey(CodigoQR, on_delete=models.SET_NULL, null=True, blank=True, related_name='campeonatos')
    activo = models.CharField(max_length=2, choices=OPCIONES_SI_NO, default='SI')
    es_publico = models.CharField(max_length=2, choices=OPCIONES_SI_NO, default='SI')
    fixture_generado = models.BooleanField(default=False)

    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")
        if self.fecha_fin_inscripcion and self.fecha_inicio and self.fecha_fin_inscripcion > self.fecha_inicio:
            raise ValidationError("La fecha de fin de inscripción no puede ser posterior a la fecha de inicio.")

    def __str__(self):
        return f"{self.nombre} ({self.deporte.nombre}) - {self.estado}"

# Modelo equipo
class Equipo(models.Model):
    GENERO_CHOICES = (('masculino', 'Masculino'), ('femenino', 'Femenino'))
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE, related_name='equipos')
    nombre = models.CharField(max_length=100)
    carrera = models.ForeignKey('Carrera', on_delete=models.PROTECT, related_name='equipos')
    logo = models.ImageField(upload_to='logos_equipos/', null=True, blank=True)
    aprobado = models.BooleanField(default=False)
    delegado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, limit_choices_to={'rol': 'DELEGADO'})
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES, default='masculino')

    class Meta:
        unique_together = ('campeonato', 'nombre')

    def __str__(self):
        return self.nombre

    def clean(self):
        if not self.nombre:
            raise ValidationError("El nombre del equipo es obligatorio.")
        if self.campeonato.estado != 'INSCRIPCION':
            raise ValidationError("El campeonato debe estar en estado de inscripción para registrar un equipo.")
        if self.delegado and self.delegado.rol != 'DELEGADO':
            raise ValidationError("El delegado debe ser un usuario con rol DELEGADO.")
        if not self.delegado:
            raise ValidationError("El equipo debe tener un delegado asignado.")
        if not self.logo:
            raise ValidationError("Debes subir el logo del equipo.")
        pago_obj = getattr(self, 'pago', None)
        if self.aprobado and (not pago_obj or pago_obj.estado != 'APROBADO'):
            raise ValidationError("No puedes aprobar el equipo sin un pago aprobado.")

    @property
    def puede_participar(self):
        pago_obj = getattr(self, 'pago', None)
        return pago_obj and pago_obj.estado == 'APROBADO'

    @cached_property
    def goles_totales(self):
        return EstadisticaJugadorFutbol.objects.filter(jugador__equipo=self).aggregate(total_goles=Sum('goles'))['total_goles'] or 0

    @cached_property
    def tarjetas_totales(self):
        stats = EstadisticaJugadorFutbol.objects.filter(jugador__equipo=self).aggregate(amarillas=Sum('tarjetas_amarillas'), rojas=Sum('tarjetas_rojas'))
        return (stats['amarillas'] or 0) + (stats['rojas'] or 0)

    @cached_property
    def puntos_totales(self):
        deporte = self.campeonato.deporte.nombre.upper()
        if deporte == 'FUTBOL':
            puntos = 0
            partidos_local = self.partidos_locales.filter(estado='FINALIZADO')
            partidos_visitante = self.partidos_visitantes.filter(estado='FINALIZADO')
            for p in partidos_local:
                if p.resultado_local > p.resultado_visitante: puntos += 3
                elif p.resultado_local == p.resultado_visitante: puntos += 1
            for p in partidos_visitante:
                if p.resultado_visitante > p.resultado_local: puntos += 3
                elif p.resultado_visitante == p.resultado_local: puntos += 1
            return puntos
        # ... (otros deportes) ...
        return 0

# Modelo jugador
class Jugador(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True, blank=True, related_name='jugadores')
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'JUGADOR'})
    numero_camiseta = models.PositiveIntegerField(null=True, blank=True)
    posicion = models.CharField(max_length=50, null=True, blank=True)
    edad = models.PositiveIntegerField()

    def clean(self):
        super().clean()
        if self.edad < 17:
            raise ValidationError("La edad mínima para un jugador es 17 años.")
        if self.equipo:
            if self.numero_camiseta is None:
                raise ValidationError("El número de camiseta es obligatorio.")
            if Jugador.objects.filter(equipo=self.equipo, numero_camiseta=self.numero_camiseta).exclude(pk=self.pk).exists():
                raise ValidationError("Ya existe un jugador con este número de camiseta en este equipo.")
            if not self.equipo.aprobado:
                raise ValidationError("No se pueden añadir jugadores a un equipo no aprobado.")
            if self.equipo.jugadores.count() >= self.equipo.campeonato.max_jugadores_por_equipo:
                raise ValidationError(f"El equipo ya tiene el máximo de jugadores permitidos.")

# Modelo Partido
class Partido(models.Model):
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE, related_name='partidos')
    equipo_local = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_locales')
    equipo_visitante = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_visitantes')
    fecha = models.DateField()
    hora = models.TimeField()
    lugar = models.CharField(max_length=100)
    resultado_local = models.PositiveIntegerField(null=True, blank=True)
    resultado_visitante = models.PositiveIntegerField(null=True, blank=True)
    ESTADOS = [
        ('PROGRAMADO', 'Programado'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADO', 'Finalizado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PROGRAMADO')
    arbitro = models.ForeignKey(Arbitro, on_delete=models.SET_NULL, null=True, blank=True)
    tarjetas_amarillas_local = models.PositiveIntegerField(default=0, null=True, blank=True)
    tarjetas_amarillas_visitante = models.PositiveIntegerField(default=0, null=True, blank=True)
    tarjetas_rojas_local = models.PositiveIntegerField(default=0, null=True, blank=True)
    tarjetas_rojas_visitante = models.PositiveIntegerField(default=0, null=True, blank=True)
    observaciones_arbitro = models.TextField(blank=True, null=True)
    suspensiones_json = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('campeonato', 'fecha', 'hora', 'equipo_local', 'equipo_visitante')

    def __str__(self):
        return f'{self.equipo_local} vs {self.equipo_visitante} - {self.campeonato.nombre}'

# Modelo Pago
class Pago(models.Model):
    equipo = models.OneToOneField(Equipo, on_delete=models.CASCADE, related_name='pago')
    metodo = models.CharField(max_length=20, choices=[('TRANSFERENCIA', 'Transferencia'), ('EFECTIVO', 'Efectivo')])
    comprobante_pago = models.ImageField(upload_to='comprobantes/', blank=True, null=True)
    estado = models.CharField(max_length=20, choices=[('PENDIENTE', 'Pendiente'), ('APROBADO', 'Aprobado'), ('RECHAZADO', 'Rechazado')], default='PENDIENTE')
    fecha_pago = models.DateTimeField(auto_now_add=True)
    observacion_admin = models.TextField(blank=True, null=True)
    codigo_qr = models.ForeignKey(CodigoQR, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f'Pago de {self.equipo.nombre} - {self.estado}'

# --- MODELOS DE ESTADÍSTICAS REFACTORIZADOS ---

class BaseEstadistica(models.Model):
    """Modelo base abstracto para estadísticas de jugadores en un campeonato."""
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    partidos_jugados = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        unique_together = ('campeonato', 'jugador')

    def __str__(self):
        return f"{self.jugador.usuario.username} - {self.campeonato.nombre}"

class EstadisticaJugadorFutbol(BaseEstadistica):
    goles = models.PositiveIntegerField(default=0)
    tarjetas_amarillas = models.PositiveIntegerField(default=0)
    tarjetas_rojas = models.PositiveIntegerField(default=0)

class EstadisticaJugadorBasquet(BaseEstadistica):
    canastas = models.PositiveIntegerField(default=0)
    rebotes = models.PositiveIntegerField(default=0)
    asistencias = models.PositiveIntegerField(default=0)

class EstadisticaJugadorAjedrez(BaseEstadistica):
    partidas_ganadas = models.PositiveIntegerField(default=0)
    partidas_empatadas = models.PositiveIntegerField(default=0)
    partidas_perdidas = models.PositiveIntegerField(default=0)

class EstadisticaJugadorEcuaboly(BaseEstadistica):
    sets_ganados = models.PositiveIntegerField(default=0)
    sets_perdidos = models.PositiveIntegerField(default=0)

class EstadisticaJugadorPingPong(BaseEstadistica):
    partidos_ganados = models.PositiveIntegerField(default=0)
    partidos_perdidos = models.PositiveIntegerField(default=0)

class EstadisticaJugadorTenis(BaseEstadistica):
    sets_ganados = models.PositiveIntegerField(default=0)
    sets_perdidos = models.PositiveIntegerField(default=0)

class EstadisticaJugadorVideojuegos(BaseEstadistica):
    partidas_ganadas = models.PositiveIntegerField(default=0)
    partidas_perdidas = models.PositiveIntegerField(default=0)

class EstadisticaJugadorFutbolin(BaseEstadistica):
    partidos_ganados = models.PositiveIntegerField(default=0)
    partidos_perdidos = models.PositiveIntegerField(default=0)
    goles = models.PositiveIntegerField(default=0)

# --- Otros modelos ---

class ImagenGaleria(TimeStampedModel):
    titulo = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='galeria/')
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.titulo

class Noticia(TimeStampedModel):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    imagen = models.ImageField(upload_to='noticias/', blank=True, null=True)

    def __str__(self):
        return self.titulo

class Testimonio(TimeStampedModel):
    autor = models.CharField(max_length=100)
    contenido = models.TextField()
    foto = models.ImageField(upload_to='testimonios/', blank=True, null=True)

    def __str__(self):
        return self.autor

class Suspension(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='suspensiones')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.TextField()

    def __str__(self):
        return f'Suspensión de {self.jugador.usuario.username}'

class Transmision(models.Model):
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE, related_name='transmisiones')
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name='transmision')
    enlace = models.URLField()
    descripcion = models.CharField(max_length=500, blank=True, null=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Transmisión"
        verbose_name_plural = "Transmisiones"
        unique_together = ('campeonato', 'partido')

    def __str__(self):
        return f'Transmisión de {self.partido}'