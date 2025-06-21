from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError

# modelo de usuario 
class Usuario(AbstractUser):
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('DELEGADO', 'Delegado de Carrera'),
        ('JUGADOR', 'Jugador'),
    ]
    # rol del usuario puede ser ADMIN, DELEGADO o JUGADOR
    rol = models.CharField(max_length=10, choices=ROLES)
    # carrera a la que pertenece el usuario si es que es delegado
    carrera = models.CharField(max_length=100, blank=True, null=True)

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

    def __str__(self):
        return f"{self.username} ({self.rol})"

# modelo deporte 
class Deporte(models.Model):
    # nombre del deporte 
    nombre = models.CharField(max_length=100, unique=True)
    # descripcion del deporte
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# modelo campeonato
class Campeonato(models.Model):
    DIAS_SEMANA = [
        ('LUNES', 'Lunes'),
        ('MARTES', 'Martes'),
        ('MIERCOLES', 'Miércoles'),
        ('JUEVES', 'Jueves'),
        ('VIERNES', 'Viernes'),
        ('SABADO', 'Sábado'),
        ('DOMINGO', 'Domingo'),
    ]
    # estados del campeonato
    Estados = [
        ('INSCRIPCION', 'Inscripción Abierta'),
        ('CERRADO', 'Inscripción Cerrada'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADO', 'Finalizado'),
    ]
    # nombre del campeonato 
    nombre = models.CharField(max_length=100, unique=True)
    # descripcion del campeonato 
    descripcion = models.TextField()
    # reglamento del campeonato
    reglamento = models.FileField(upload_to='reglamentos/', blank=True, null=True)
    # fecha de inicio del campeonato
    fecha_inicio = models.DateField()
    # fecha de fin del campeonato
    fecha_fin = models.DateField()
    # estado del campeonato
    estado = models.CharField(max_length=20, choices=Estados, default='INSCRIPCION')
    # deporte al que pertenece el campeonato
    deporte = models.ForeignKey(Deporte, on_delete=models.CASCADE, related_name='campeonatos')
    # delegado del campeonato
    delegado = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='campeonatos_delegado', blank=True, null=True)
    # dias q se juega el campeonato
    dias_partido = MultiSelectField(choices=DIAS_SEMANA, blank=True, default=[])

    def clean(self):
        # Validación para que la fecha fin no sea menor que la fecha inicio
        if self.fecha_fin < self.fecha_inicio:
            raise ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")

    def __str__(self):
        return f"{self.nombre} ({self.deporte.nombre}) - {self.estado}"

# modelo equipo
class Equipo(models.Model):
    # campeonato al que pertenece el equipo relacion de uno a muchos
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE, related_name='equipos')
    # nombre del equipo
    nombre = models.CharField(max_length=100)
    # carrera a la que pertenece el equipo
    carrera = models.CharField(max_length=100, blank=True, null=True)
    # logo del equipo si es que quieren subir uno
    logo = models.ImageField(upload_to='logos_equipos/', blank=True, null=True)
    # indica si el equipo esta aprobado para participar o no 
    aprobado = models.BooleanField(default=False)
    # delegado que registro el equipo debe ser un usuario con rol de delegado
    delegado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, limit_choices_to={'rol': 'DELEGADO'})

    class Meta:
        # Un equipo debe tener nombre único dentro de un mismo campeonato
        unique_together = ('campeonato', 'nombre')

    def __str__(self):
        return self.nombre

# modelo jugador
class Jugador(models.Model):
    # equipo al que pertenece el jugador relacion de uno a muchos
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='jugadores')
    # usuario que representa al jugador relacion de uno a uno solo jugador
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'JUGADOR'})
    # numero de camiseta del jugador 
    numero_camiseta = models.PositiveIntegerField()
    # edad del jugador 
    edad = models.PositiveIntegerField()
    # goles anotados por el jugador por defecto serian cero
    goles = models.PositiveIntegerField(default=0)
    # puntos anotados por el jugador por defecto serian cero
    puntos = models.PositiveIntegerField(default=0)
    # canastas anotadas por el jugador por defecto serian cero en basquetbol
    canastas = models.PositiveIntegerField(default=0)
    # tarjetas amarillas recibidas por el jugador por defecto serian cero
    tarjetas_amarillas = models.PositiveIntegerField(default=0)
    # tarjetas rojas recibidas por el jugador por defecto serian cero
    tarjetas_rojas = models.PositiveIntegerField(default=0)

    class Meta:
        # Un jugador no puede repetir número de camiseta en el mismo equipo
        unique_together = ('equipo', 'numero_camiseta')

    def clean(self):
        # Validación para edad mínima 
        if self.edad < 17:
            raise ValidationError("La edad mínima para un jugador es 17 años.")

    def __str__(self):
        return f"{self.usuario.username} ({self.equipo.nombre})"

# modelo arbitro
class Arbitro(models.Model):
    # nombre del arbitro 
    nombre = models.CharField(max_length=100)
    # apellido del arbitro
    apellido = models.CharField(max_length=100)
    # experiencia del arbitro 
    experiencia = models.TextField()
    # deportes que arbitra relacion de muchos a muchos
    deportes = models.ManyToManyField(Deporte, related_name='arbitros')
    # informacion de contacto del arbitro
    contacto = models.CharField(max_length=100)
    # estado del arbitro si esta activo o no
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# modelo partido
class Partido(models.Model):
    # campeonato al que pertenece el partido relacion de uno a muchos
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE, related_name='partidos')
    # equipo local que juega el partido relacion de uno a muchos
    equipo_local = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_locales')
    # equipo visitante que juega el partido relacion de uno a muchos
    equipo_visitante = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_visitantes')
    # fecha del partido
    fecha = models.DateField()
    # hora del partido
    hora = models.TimeField()
    # lugar donde se juega el partido
    lugar = models.CharField(max_length=100)
    # arbitro que dirige el partido relacion de uno a muchos
    arbitro = models.ForeignKey(Arbitro, on_delete=models.SET_NULL, null=True)
    # resultado de goles del equipo local este puede estar vacio
    resultado_local = models.PositiveIntegerField(default=0, blank=True, null=True)
    # resultado de goles del equipo visitante este puede estar vacio
    resultado_visitante = models.PositiveIntegerField(default=0, blank=True, null=True)
    # estado del partido si esta programado, en curso o finalizado
    ESTADOS_PARTIDO = [
        ('PROGRAMADO', 'Programado'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADO', 'Finalizado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS_PARTIDO, default='PROGRAMADO')

    class Meta:
        # Un partido es único por campeonato, fecha, hora, y equipos que juegan
        unique_together = ('campeonato', 'fecha', 'hora', 'equipo_local', 'equipo_visitante')

    def clean(self):
        # Validar que la fecha esté dentro del rango del campeonato
        if self.fecha < self.campeonato.fecha_inicio or self.fecha > self.campeonato.fecha_fin:
            raise ValidationError("La fecha del partido debe estar dentro del rango del campeonato.")
        # Validar que el equipo local y visitante no sean el mismo
        if self.equipo_local == self.equipo_visitante:
            raise ValidationError("El equipo local y visitante no pueden ser el mismo.")

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} - {self.fecha}"

# modelo de estadisticas generales del campeonato
class EstadisticasCampeonato(models.Model):
    # campeonato al que pertenecen las estadisticas relacion de uno a uno
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE, related_name='estadisticas')
    # equipo al que corresponde esta estadistica 
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='estadisticas')
    # partidos jugados por el equipo
    partidos_jugados = models.PositiveIntegerField(default=0)
    # partidos ganados por el equipo
    partidos_ganados = models.PositiveIntegerField(default=0)
    # partidos empatados por el equipo
    partidos_empatados = models.PositiveIntegerField(default=0)
    # partidos perdidos por el equipo
    partidos_perdidos = models.PositiveIntegerField(default=0)
    # goles anotados por el equipo
    goles_anotados = models.PositiveIntegerField(default=0)
    # goles recibidos por el equipo
    goles_recibidos = models.PositiveIntegerField(default=0)
    # puntos obtenidos por el equipo
    puntos_obtenidos = models.PositiveIntegerField(default=0)
    # canastas anotadas por el equipo (en caso de deportes como basquetbol)
    canastas_anotadas = models.PositiveIntegerField(default=0)
    # tarjetas amarillas recibidas por el equipo
    tarjetas_amarillas = models.PositiveIntegerField(default=0)
    # tarjetas rojas recibidas por el equipo
    tarjetas_rojas = models.PositiveIntegerField(default=0)
    
    class Meta:
        # Una estadística es única para la pareja campeonato-equipo
        unique_together = ('campeonato', 'equipo')

    def clean(self):
        # Validar que suma partidos ganados, empatados y perdidos no sea mayor que partidos jugados
        if self.partidos_ganados + self.partidos_empatados + self.partidos_perdidos > self.partidos_jugados:
            raise ValidationError("La suma de partidos ganados, empatados y perdidos no puede ser mayor que los partidos jugados.")
        # Validar que goles anotados y recibidos no sean negativos (aunque PositiveIntegerField ya lo impide, por seguridad)
        if self.goles_anotados < 0 or self.goles_recibidos < 0:
            raise ValidationError("Los goles anotados y recibidos no pueden ser negativos.")
        # Validar que canastas no sean negativas
        if self.canastas_anotadas < 0:
            raise ValidationError("Las canastas anotadas no pueden ser negativas.")
        # Validar tarjetas amarillas y rojas no negativas
        if self.tarjetas_amarillas < 0 or self.tarjetas_rojas < 0:
            raise ValidationError("Las tarjetas amarillas y rojas no pueden ser negativas.")

    def __str__(self):
        return f"{self.campeonato.nombre} - {self.equipo.nombre} - {self.puntos_obtenidos} pts"
