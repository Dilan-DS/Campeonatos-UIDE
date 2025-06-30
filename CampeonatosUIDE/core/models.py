from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Q # Importar Q para consultas complejas

# Modelo personalizado de usuario
class Usuario(AbstractUser):
    # Definición de roles posibles
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('DELEGADO', 'Delegado de Carrera'),
        ('JUGADOR', 'Jugador'),
    ]
    # Campo para rol del usuario (ADMIN, DELEGADO o JUGADOR)
    rol = models.CharField(max_length=10, choices=ROLES)
    # Carrera a la que pertenece el usuario (opcional para delegados)
    carrera = models.CharField(max_length=100, blank=True, null=True)

    # Relación con grupos para permisos (ManyToMany)
    groups = models.ManyToManyField(
        Group,
        related_name='usuarios_custom',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
        related_query_name='usuario_custom',
    )

    # Relación con permisos específicos (ManyToMany)
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuarios_custom',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
        related_query_name='usuario_custom',
    )

    # Representación en texto del usuario
    def __str__(self):
        return f"{self.username} ({self.rol})"

# Modelo de deporte
class Deporte(models.Model):
    # Nombre único del deporte
    nombre = models.CharField(max_length=100, unique=True)
    # Descripción opcional del deporte
    descripcion = models.TextField(blank=True, null=True)

    # Representación en texto del deporte
    def __str__(self):
        return self.nombre

# Modelo para guardar códigos QR de bancos o métodos de transferencia que sube el admin
class CodigoQR(models.Model):
    # Nombre del banco o método (ej: Banco Pichincha)
    banco = models.CharField(max_length=100, unique=True)
    # Imagen del código QR subida por admin
    imagen_qr = models.ImageField(upload_to='codigos_qr/')
    # Descripción opcional para detalles extra
    descripcion = models.TextField(blank=True, null=True)

    # Representación en texto con el nombre del banco
    def __str__(self):
        return self.banco

    # Validaciones del modelo
    def clean(self):
        # Validar que la imagen QR esté presente
        if not self.imagen_qr:
            raise ValidationError("La imagen del código QR es obligatoria.")
        # Validar longitud máxima de la descripción
        if self.descripcion and len(self.descripcion) > 500:
            raise ValidationError("La descripción no puede exceder los 500 caracteres.")

    # Metadatos para admin
    class Meta:
        verbose_name = "Código QR"
        verbose_name_plural = "Códigos QR"

class TipoCampeonato(models.Model):
    # Nombre único del tipo de campeonato ( Fútbol, Básquet, etc.)
    nombre = models.CharField(max_length=30, unique=True)
    # Descripción opcional del tipo de campeonato
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo de Campeonato"
        verbose_name_plural = "Tipos de Campeonato"
# Modelo campeonato
class Campeonato(models.Model):
    # Opciones para días de la semana donde se juega
    DIAS_SEMANA = [
        ('LUNES', 'Lunes'),
        ('MARTES', 'Martes'),
        ('MIERCOLES', 'Miércoles'),
        ('JUEVES', 'Jueves'),
        ('VIERNES', 'Viernes'),
        ('SABADO', 'Sábado'),
        ('DOMINGO', 'Domingo'),
    ]
    # Estados posibles del campeonato
    ESTADOS = [
        ('INSCRIPCION', 'Inscripción Abierta'),
        ('CERRADO', 'Inscripción Cerrada'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADO', 'Finalizado'),
    ]

    # Nombre único del campeonato
    nombre = models.CharField(max_length=100, unique=True)
    # Tipo de campeonato (FK a TipoCampeonato)
    tipo_campeonato = models.ForeignKey(TipoCampeonato, on_delete=models.SET_NULL, null=True, blank=True, related_name='campeonatos')

    # Descripción del campeonato
    descripcion = models.TextField()
    # Reglamento en archivo (PDF u otro), opcional
    reglamento = models.FileField(upload_to='reglamentos/', blank=True, null=True)
    # Fecha de inicio del campeonato
    fecha_inicio = models.DateField()
    # Fecha de fin del campeonato
    fecha_fin = models.DateField()
    # Estado actual del campeonato
    estado = models.CharField(max_length=20, choices=ESTADOS, default='INSCRIPCION')
    # Deporte asociado al campeonato (FK)
    deporte = models.ForeignKey(Deporte, on_delete=models.CASCADE, related_name='campeonatos')
    # Delegado asignado (usuario con rol delegado), opcional
    delegado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, related_name='campeonatos_delegado', blank=True, null=True)
    # Días de la semana que se juegan los partidos (multi-select)
    dias_partido = MultiSelectField(choices=DIAS_SEMANA, blank=True, default=[])
    # Numero de jugadores por equipo
    # En Campeonato
    max_jugadores_por_equipo = models.PositiveIntegerField(default=11, help_text="Cantidad máxima de jugadores por equipo en este campeonato")
    # Precio que debe pagar cada equipo para inscribirse
    precio_inscripcion = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    # Validación para que la fecha fin no sea anterior a la fecha inicio
    def clean(self):
        if self.fecha_fin < self.fecha_inicio:
            raise ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")

    # Representación en texto del campeonato
    def __str__(self):
        return f"{self.nombre} ({self.deporte.nombre}) - {self.estado}"

# Modelo equipo
class Equipo(models.Model):
    # Campeonato al que pertenece el equipo (FK)
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE, related_name='equipos')
    # Nombre del equipo
    nombre = models.CharField(max_length=100)
    # Carrera a la que pertenece el equipo (opcional)
    carrera = models.CharField(max_length=100, blank=True, null=True)
    # Logo del equipo (imagen opcional)
    logo = models.ImageField(upload_to='logos_equipos/', blank=True, null=True)
    # Indicador si el equipo está aprobado para participar
    aprobado = models.BooleanField(default=False)
    # Delegado que registró el equipo (debe ser rol DELEGADO)
    delegado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, limit_choices_to={'rol': 'DELEGADO'})

    def clean(self):
        # Validar que el nombre del equipo no esté vacío
        if not self.nombre:
            raise ValidationError("El nombre del equipo es obligatorio.")
        # Validar que el nombre del equipo no exceda los 100 caracteres
        if len(self.nombre) > 100:
            raise ValidationError("El nombre del equipo no puede exceder los 100 caracteres.")
        # Validar que el campeonato esté abierto para inscripción
        if self.campeonato.estado != 'INSCRIPCION':
            raise ValidationError("El campeonato debe estar en estado de inscripción para registrar un equipo.")
        # Validar que el delegado sea un usuario con rol DELEGADO
        if self.delegado and self.delegado.rol != 'DELEGADO':
            raise ValidationError("El delegado debe ser un usuario con rol DELEGADO.")
        # Validar que el equipo tenga delegado asignado
        if not self.delegado:
            raise ValidationError("El equipo debe tener un delegado asignado.")

        # VALIDACIÓN MEJORADA: Si se quiere aprobar el equipo, debe tener pago aprobado
        # Usar getattr para acceder a 'pago' de forma segura y evitar AttributeError
        pago_obj = getattr(self, 'pago', None)
        if self.aprobado and (not pago_obj or pago_obj.estado != 'APROBADO'):
            raise ValidationError("No puedes aprobar el equipo sin un pago aprobado o si no tiene un pago asociado.")

    # Restricción: nombre único dentro del mismo campeonato
    class Meta:
        unique_together = ('campeonato', 'nombre')

    # Representación en texto del equipo
    def __str__(self):
        return self.nombre

    # Propiedad que indica si el equipo puede participar (pago aprobado)
    @property
    def puede_participar(self):
        # Usar getattr para acceder a 'pago' de forma segura
        pago_obj = getattr(self, 'pago', None)
        return pago_obj and pago_obj.estado == 'APROBADO'

# Modelo jugador
class Jugador(models.Model):
    # Equipo al que pertenece el jugador (FK)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='jugadores')
    # Usuario que representa al jugador (rol JUGADOR)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'JUGADOR'})
    # Número de camiseta (único en equipo)
    numero_camiseta = models.PositiveIntegerField()
    # Edad del jugador
    edad = models.PositiveIntegerField()

    # Restricción de número único en el equipo
    class Meta:
        unique_together = ('equipo', 'numero_camiseta')

    # Validación edad mínima 17 años y equipo aprobado
    def clean(self):
        if self.edad < 17:
            raise ValidationError("La edad mínima para un jugador es 17 años.")
        if self.equipo and not self.equipo.aprobado:
            raise ValidationError("No se pueden añadir jugadores a un equipo no aprobado.")
            
        # VALIDACIÓN MEJORADA: no sobrepasar el número máximo permitido de jugadores.
        # El conteo de jugadores debería excluir el jugador actual si está editando.
        campeonato = self.equipo.campeonato
        
        # Iniciar el queryset para contar jugadores
        jugadores_en_equipo = self.equipo.jugadores.all()
        
        # Si el jugador está siendo editado (ya tiene un PK), excluirlo del conteo para no contarlo doble
        if self.pk:
            jugadores_en_equipo = jugadores_en_equipo.exclude(pk=self.pk)

        cantidad_actual = jugadores_en_equipo.count()

        # Validar si al agregar/mover este jugador se excede el límite
        if cantidad_actual >= campeonato.max_jugadores_por_equipo:
            raise ValidationError(f"Este equipo ya tiene el máximo permitido de {campeonato.max_jugadores_por_equipo} jugadores.")


    # Representación en texto del jugador
    def __str__(self):
        return f"{self.usuario.username} ({self.equipo.nombre})"

    # MÉTODO MEJORADO: Verificar si el jugador está suspendido
    def esta_suspendido(self):
        return self.suspensiones.filter(
            fecha_inicio__lte=timezone.now().date(),
            fecha_fin__gte=timezone.now().date()
        ).exists()

# Modelo árbitro
class Arbitro(models.Model):
    # Nombre y apellido
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    # Experiencia en texto
    experiencia = models.TextField()
    # Deportes que arbitra (ManyToMany)
    deportes = models.ManyToManyField(Deporte, related_name='arbitros')
    # Información de contacto
    contacto = models.CharField(max_length=100)
    # Estado activo/inactivo
    estado = models.BooleanField(default=True)

    # Representación en texto del árbitro
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# Modelo partido
class Partido(models.Model):
    # Campeonato (FK)
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE, related_name='partidos')
    # Equipos local y visitante (FK)
    equipo_local = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_locales')
    equipo_visitante = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_visitantes')
    # Fecha y hora del partido
    fecha = models.DateField()
    hora = models.TimeField()
    # Lugar donde se juega
    lugar = models.CharField(max_length=100)
    # Árbitro asignado (FK), opcional
    arbitro = models.ForeignKey(Arbitro, on_delete=models.SET_NULL, null=True, blank=True)
    # Resultados de goles pueden ser null si el partido no ha terminado
    resultado_local = models.PositiveIntegerField(blank=True, null=True)
    resultado_visitante = models.PositiveIntegerField(blank=True, null=True)
    # Estados posibles del partido
    ESTADOS_PARTIDO = [
        ('PROGRAMADO', 'Programado'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADO', 'Finalizado'),
    ]
    # Estado actual del partido
    estado = models.CharField(max_length=20, choices=ESTADOS_PARTIDO, default='PROGRAMADO')

    # Restricción única para evitar partidos duplicados en la misma fecha y hora con los mismos equipos
    class Meta:
        unique_together = ('campeonato', 'fecha', 'hora', 'equipo_local', 'equipo_visitante')

    # Validaciones para fecha y equipos
    def clean(self):
        super().clean()
        
        # Validar fecha dentro del campeonato
        if self.fecha < self.campeonato.fecha_inicio or self.fecha > self.campeonato.fecha_fin:
            raise ValidationError("La fecha del partido debe estar dentro del rango del campeonato.")
        
        # Validar equipos diferentes
        if self.equipo_local == self.equipo_visitante:
            raise ValidationError("El equipo local y visitante no pueden ser el mismo.")
        
        # Validar que el día del partido esté dentro de los días permitidos del campeonato
        dia_semana = self.fecha.strftime('%A').upper() 
        # Mapeo para tus días en español
        dias_semana_map = {
            'MONDAY': 'LUNES',
            'TUESDAY': 'MARTES',
            'WEDNESDAY': 'MIERCOLES',
            'THURSDAY': 'JUEVES',
            'FRIDAY': 'VIERNES',
            'SATURDAY': 'SABADO',
            'SUNDAY': 'DOMINGO',
        }
        dia_espanol = dias_semana_map.get(dia_semana)
        if dia_espanol not in self.campeonato.dias_partido:
            raise ValidationError(f"El día del partido ({dia_espanol}) no está permitido en el campeonato.")

        # ya tiene un partido programado (como local o visitante) en la misma fecha y hora
        conflictos = Partido.objects.filter(
            campeonato=self.campeonato,
            fecha=self.fecha,
            hora=self.hora
        ).filter(
            Q(equipo_local=self.equipo_local) | Q(equipo_visitante=self.equipo_local) | 
            Q(equipo_local=self.equipo_visitante) | Q(equipo_visitante=self.equipo_visitante)
        ).exclude(pk=self.pk) # Excluir el partido actual si está siendo editado

        if conflictos.exists():
            raise ValidationError("Alguno de los equipos ya tiene un partido programado en esta fecha y hora.")
        
        conflicto_lugar = Partido.objects.filter(
            campeonato=self.campeonato,
            fecha=self.fecha,
            hora=self.hora,
            lugar__iexact=self.lugar
        ).exclude(pk=self.pk)

        if conflicto_lugar.exists():
            raise ValidationError("Ya hay un partido programado en este lugar, fecha y hora.")
    # Representación en texto del partido
    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} - {self.fecha}"

# Modelo de transmisión en vivo
class Transmision(models.Model):
    # Campeonato (FK)
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE, related_name='transmisiones')
    # Partido (FK)
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name='transmision')
    # URL de la transmisión
    enlace = models.URLField()
    # Descripción opcional (CAMPO MEJORADO: CharField con max_length)
    descripcion = models.CharField(max_length=500, blank=True, null=True)
    # Indicador si la transmisión está activa
    activa = models.BooleanField(default=True)

    # Metadatos para admin
    class Meta:
        verbose_name = "Transmisión"
        verbose_name_plural = "Transmisiones"
        unique_together = ('campeonato', 'partido')

    # Validaciones del modelo
    def clean(self):
        if not self.enlace:
            raise ValidationError("El enlace de la transmisión no puede estar vacío.")
        # La validación de longitud máxima del CharField ya la maneja Django automáticamente,
        # pero la mantenemos aquí como una validación extra si se prefiere un mensaje personalizado.
        if self.descripcion and len(self.descripcion) > 500:
            raise ValidationError("La descripción no puede exceder los 500 caracteres.")

    # Representación en texto de la transmisión
    def __str__(self):
        return f"Transmisión de {self.partido} - {'Activa' if self.activa else 'Inactiva'}"

# Modelo pago del equipo
class Pago(models.Model):
    # Métodos de pago permitidos
    METODOS = [
        ('TRANSFERENCIA', 'Transferencia'),
        ('EFECTIVO', 'Efectivo'),
    ]
    # Estados del pago
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    # Equipo que realiza el pago (OneToOne)
    equipo = models.OneToOneField(Equipo, on_delete=models.CASCADE, related_name='pago')
    # Método de pago seleccionado (transferencia o efectivo)
    metodo = models.CharField(max_length=20, choices=METODOS)
    # Banco elegido por el delegado si es transferencia (FK a CodigoQR)
    codigo_qr = models.ForeignKey(CodigoQR, on_delete=models.SET_NULL, null=True, blank=True)
    # Imagen comprobante del pago (subida por delegado)
    comprobante_pago = models.ImageField(upload_to='comprobantes/', blank=True, null=True)
    # Estado del pago
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    # Fecha y hora de registro del pago
    fecha_pago = models.DateTimeField(auto_now_add=True)
    # Observaciones que puede dejar el admin sobre el pago
    observacion_admin = models.TextField(blank=True, null=True)

    # Validaciones del pago
    def clean(self):
        # Si el método es transferencia, se debe elegir banco (codigo_qr)
        if self.metodo == 'TRANSFERENCIA' and not self.codigo_qr:
            raise ValidationError("Debe seleccionar el banco para transferencia.")
        # Validar estado válido
        if self.estado not in dict(self.ESTADOS).keys():
            raise ValidationError(f"Estado inválido: {self.estado}")
        # Si el estado es aprobado o rechazado, debe haber comprobante de pago
        if self.estado in ['APROBADO', 'RECHAZADO'] and not self.comprobante_pago:
            raise ValidationError("Debe subir el comprobante de pago cuando el pago está aprobado o rechazado.")

    # Representación en texto del pago con banco si aplica
    def __str__(self):
        if self.metodo == 'TRANSFERENCIA':
            banco = self.codigo_qr.banco if self.codigo_qr else 'Sin banco'
            return f"{self.equipo.nombre} - Transferencia ({banco}) - {self.estado}"
        return f"{self.equipo.nombre} - Efectivo - {self.estado}"

    # Metadatos para admin
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
# Señal para actualizar estado del equipo al cambiar el estado del pago
@receiver(post_save, sender=Pago)
def actualizar_estado_equipo(sender, instance, **kwargs):
    equipo = instance.equipo
    if instance.estado == 'APROBADO' and not equipo.aprobado:
        equipo.aprobado = True
        equipo.save()
    elif instance.estado == 'RECHAZADO' and equipo.aprobado:
        equipo.aprobado = False
        equipo.save()

class Suspension(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='suspensiones')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.TextField()

    def clean(self):
        if self.fecha_fin < self.fecha_inicio:
            raise ValidationError("La fecha fin debe ser posterior a la fecha inicio.")

    def esta_activa(self):
        hoy = timezone.now().date()
        return self.fecha_inicio <= hoy <= self.fecha_fin

    def __str__(self):
        return f"Suspensión de {self.jugador.usuario.username} desde {self.fecha_inicio} hasta {self.fecha_fin}"
# Modelo de estadísticas para fútbol
class EstadisticaFutbol(models.Model):
    # Relación con campeonato y equipo
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    # Relación con equipo
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    # Estadísticas específicas del fútbol
    # Partidos jugados, goles, tarjetas amarillas y rojas, puntos
    partidos_jugados = models.PositiveIntegerField(default=0)
    goles = models.PositiveIntegerField(default=0)
    tarjetas_amarillas = models.PositiveIntegerField(default=0)
    tarjetas_rojas = models.PositiveIntegerField(default=0)
    puntos = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('campeonato', 'equipo')

    def __str__(self):
        return f"Futbol: {self.equipo.nombre} - {self.campeonato.nombre}"

# Modelo de estadísticas para básquet
class EstadisticaBasquet(models.Model):
    # Relación con campeonato y equipo
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    # Relación con equipo
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    # Estadísticas específicas del básquet
    # Partidos jugados, canastas, rebotes, asistencias, puntos  por defecto son en 0
    # Estos campos se pueden actualizar a medida que avanza el campeonato
    partidos_jugados = models.PositiveIntegerField(default=0)  
    canastas = models.PositiveIntegerField(default=0)
    rebotes = models.PositiveIntegerField(default=0)
    asistencias = models.PositiveIntegerField(default=0)
    puntos = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('campeonato', 'equipo')

    def __str__(self):
        return f"Basquet: {self.equipo.nombre} - {self.campeonato.nombre}"

# Modelo de estadísticas para ajedrez
class EstadisticaAjedrez(models.Model):
    # Relación con campeonato y equipo
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    # Relación con equipo
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    # Estadísticas específicas del ajedrez
    # Partidas jugadas, ganadas, empatadas, perdidas, puntos por defecto son en 0
    # Estos campos se pueden actualizar a medida que avanza el campeonato
    partidas_jugadas = models.PositiveIntegerField(default=0)
    partidas_ganadas = models.PositiveIntegerField(default=0)
    partidas_empatadas = models.PositiveIntegerField(default=0)
    partidas_perdidas = models.PositiveIntegerField(default=0)
    puntos = models.PositiveIntegerField(default=0)

    class Meta:
    # Restricción única para evitar duplicados de estadísticas por campeonato y equipo
        unique_together = ('campeonato', 'equipo')

    def __str__(self):
        # Representación en texto de las estadísticas de ajedrez
        # Incluye el nombre del equipo y del campeonato
        return f"Ajedrez: {self.equipo.nombre} - {self.campeonato.nombre}"

# Modelo de estadísticas para ecuaboly
class EstadisticaEcuaboly(models.Model):
    # Relación con campeonato y equipo
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    # Relación con equipo
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    # Estadísticas específicas del ecuaboly
    # Sets ganados, perdidos, partidos ganados y puntos por defecto son en 0
    # Estos campos se pueden actualizar a medida que avanza el campeonato
    sets_ganados = models.PositiveIntegerField(default=0)
    sets_perdidos = models.PositiveIntegerField(default=0)
    partidos_ganados = models.PositiveIntegerField(default=0)
    puntos = models.PositiveIntegerField(default=0)

    class Meta:
        # Restricción única para evitar duplicados de estadísticas por campeonato y equipo
        unique_together = ('campeonato', 'equipo')

    def __str__(self):
        # Representación en texto de las estadísticas de ecuaboly
        # Incluye el nombre del equipo y del campeonato
        return f"Ecuaboly: {self.equipo.nombre} - {self.campeonato.nombre}"

# Modelo de estadísticas para ping pong
class EstadisticaPingPong(models.Model):
    # Relación con campeonato y equipo
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    # Relación con equipo 
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    # Estadísticas específicas del ping pong
    # Partidos ganados, perdidos y puntos por defecto son en 0
    # Estos campos se pueden actualizar a medida que avanza el campeonato
    partidos_ganados = models.PositiveIntegerField(default=0)
    partidos_perdidos = models.PositiveIntegerField(default=0)
    puntos = models.PositiveIntegerField(default=0)

    class Meta:
        # Restricción única para evitar duplicados de estadísticas por campeonato y equipo
        # Esto asegura que cada equipo tenga una única entrada de estadísticas por campeonato
        unique_together = ('campeonato', 'equipo')

    def __str__(self):
        # Representación en texto de las estadísticas de ping pong
        # Incluye el nombre del equipo y del campeonato
        return f"Ping Pong: {self.equipo.nombre} - {self.campeonato.nombre}"

# Modelo de estadísticas para futbolín
class EstadisticaFutbolin(models.Model):
    # Relación con campeonato y equipo
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    # Relación con equipo
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    # Estadísticas específicas del futbolín
    # Partidos ganados, perdidos, goles y puntos por defecto son en 0
    # Estos campos se pueden actualizar a medida que avanza el campeonato
    partidos_ganados = models.PositiveIntegerField(default=0)
    partidos_perdidos = models.PositiveIntegerField(default=0)
    goles = models.PositiveIntegerField(default=0)
    puntos = models.PositiveIntegerField(default=0)

    class Meta:
        # Restricción única para evitar duplicados de estadísticas por campeonato y equipo
        unique_together = ('campeonato', 'equipo')

    def __str__(self):
        # Representación en texto de las estadísticas de futbolín
        return f"Futbolin: {self.equipo.nombre} - {self.campeonato.nombre}"

# Modelo de estadísticas para tenis
class EstadisticaTenis(models.Model):
    # Relación con campeonato y equipo
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    # Relación con equipo
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    # Estadísticas específicas del tenis
    # Sets ganados, perdidos, partidos ganados y puntos por defecto son en 0
    # Estos campos se pueden actualizar a medida que avanza el campeonato
    sets_ganados = models.PositiveIntegerField(default=0)
    sets_perdidos = models.PositiveIntegerField(default=0)
    partidos_ganados = models.PositiveIntegerField(default=0)
    puntos = models.PositiveIntegerField(default=0)

    class Meta: 
        # Restricción única para evitar duplicados de estadísticas por campeonato y equipo
        unique_together = ('campeonato', 'equipo')

    def __str__(self):
        # Representación en texto de las estadísticas de tenis
        return f"Tenis: {self.equipo.nombre} - {self.campeonato.nombre}"

# Modelo de estadísticas para videojuegos
class EstadisticaVideojuegos(models.Model):
    # Relación con campeonato y equipo
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    # Relación con equipo
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    # Estadísticas específicas de videojuegos
    # Partidas jugadas, ganadas, perdidas y puntos por defecto son en 0
    # Estos campos se pueden actualizar a medida que avanza el campeonato
    partidas_ganadas = models.PositiveIntegerField(default=0)
    partidas_perdidas = models.PositiveIntegerField(default=0)
    puntos = models.PositiveIntegerField(default=0)
    partidas_jugadas = models.PositiveIntegerField(default=0)


    class Meta:
        # Restricción única para evitar duplicados de estadísticas por campeonato y equipo
        # Esto asegura que cada equipo tenga una única entrada de estadísticas por campeonato
        unique_together = ('campeonato', 'equipo')

    def __str__(self):
        return f"Videojuegos: {self.equipo.nombre} - {self.campeonato.nombre}"
