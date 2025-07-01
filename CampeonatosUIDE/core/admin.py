from django.contrib import admin  
from .forms import EquipoForm
from .models import *
from django.contrib.auth.admin import UserAdmin

class CarreraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)

# Registra el modelo Usuario para poder gestionarlo desde el panel de administración

class UsuarioAdmin(UserAdmin):
    # Campos que se mostrarán en la lista
    list_display = ('username', 'first_name', 'last_name', 'email', 'rol', 'carrera', 'is_staff', 'is_active')
    # Campos por los que se puede buscar
    search_fields = ('username', 'first_name', 'last_name', 'email', 'rol', 'carrera')
    # Filtros laterales
    list_filter = ('rol', 'carrera', 'is_staff', 'is_active', 'is_superuser')
    # Campos por los que se ordena por defecto
    ordering = ('username',)

    # Campos visibles al editar un usuario
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email', 'rol', 'carrera')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    # Campos usados al crear un nuevo usuario desde el admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'rol', 'carrera', 'password1', 'password2'),
        }),
    )

# Registra el modelo Deporte como Fútbol, Básquet, etc.

class DeporteAdmin(admin.ModelAdmin):
    # Muestra el nombre y descripción en la lista
    list_display = ('nombre', 'descripcion')
    # Permite buscar por nombre
    search_fields = ('nombre',)
    # Ordena alfabéticamente por nombre
    ordering = ('nombre',)



class CampeonatoAdmin(admin.ModelAdmin):
    # Campos que se muestran en la lista
    list_display = ('nombre', 'deporte', 'tipo_campeonato', 'fecha_inicio', 'fecha_fin', 'estado', 'delegado')
    # Campos que se pueden buscar
    search_fields = ('nombre', 'descripcion', 'deporte__nombre', 'delegado__username')
    # Filtros en el panel lateral
    list_filter = ('estado', 'deporte', 'tipo_campeonato', 'dias_partido')
    # Orden por defecto
    ordering = ('fecha_inicio',)


class EquipoAdmin(admin.ModelAdmin):
    form = EquipoForm
    # Mostrar campos clave en la lista
    list_display = ('nombre', 'campeonato', 'carrera', 'aprobado', 'delegado', 'puede_participar')
    # Campos de búsqueda
    search_fields = ('nombre', 'carrera', 'delegado__username', 'campeonato__nombre')
    # Filtros por estado de aprobación y campeonato
    list_filter = ('aprobado', 'campeonato', 'carrera')
    # Orden por nombre de equipo
    ordering = ('nombre',)
    # Mostrar el logo como solo lectura para evitar ediciones accidentales
    # readonly_fields = ('logo',)



class JugadorAdmin(admin.ModelAdmin):
    # Muestra en la tabla de administración
    list_display = ('usuario', 'equipo', 'numero_camiseta', 'edad', 'esta_suspendido')
    
    # Campos de búsqueda por nombre de usuario y equipo
    search_fields = ('usuario__username', 'equipo__nombre')
    
    # Filtros por equipo y edad
    list_filter = ('equipo', 'edad')
    
    # Ordenar por número de camiseta
    ordering = ('equipo', 'numero_camiseta')
    def esta_suspendido(self, obj):
        return "Sí" if obj.esta_suspendido() else "No"
    esta_suspendido.short_description = '¿Suspendido?'




class ArbitroAdmin(admin.ModelAdmin):
    # Qué campos se muestran en la lista del admin
    list_display = ('nombre', 'apellido', 'contacto', 'mostrar_deportes', 'estado')

    # Campos por los que se puede buscar
    search_fields = ('nombre', 'apellido', 'contacto')

    # Filtros laterales
    list_filter = ('estado', 'deportes')

    # Orden por apellido
    ordering = ('apellido',)

    def mostrar_deportes(self, obj):
        return ", ".join([d.nombre for d in obj.deportes.all()])
    mostrar_deportes.short_description = 'Deportes'




class PartidoAdmin(admin.ModelAdmin):
    # Campos que se muestran en la lista del panel
    list_display = (
        'campeonato',
        'equipo_local',
        'equipo_visitante',
        'fecha',
        'hora',
        'lugar',
        'arbitro',
        'estado',
        'resultado_local',
        'resultado_visitante',
    )

    # Filtros laterales
    list_filter = ('estado', 'fecha', 'campeonato', 'arbitro')

    # Campos de búsqueda
    search_fields = (
        'equipo_local__nombre',
        'equipo_visitante__nombre',
        'campeonato__nombre',
        'lugar',
    )

    # Orden por defecto
    ordering = ('-fecha', 'hora')

    # Para mostrar la hora con formato si deseas
    def formatted_hora(self, obj):
        return obj.hora.strftime('%H:%M')
    formatted_hora.short_description = 'Hora'



class CodigoQRAdmin(admin.ModelAdmin):
    # Muestra estos campos en la lista del admin
    list_display = ('banco', 'imagen_qr', 'descripcion')
    # Permite buscar por nombre del banco
    search_fields = ('banco',)
    # Ordena alfabéticamente por nombre de banco
    ordering = ('banco',)



class TransmisionAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista del admin
    list_display = ('partido', 'campeonato', 'enlace', 'activa')
    
    # Filtros laterales
    list_filter = ('activa', 'campeonato', 'partido__fecha')
    
    # Campos de búsqueda
    search_fields = ('campeonato__nombre', 'partido__equipo_local__nombre', 'partido__equipo_visitante__nombre')
    
    # Orden por defecto
    ordering = ('-partido__fecha',)




class PagoAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista
    list_display = ('equipo', 'metodo', 'estado', 'codigo_qr', 'fecha_pago', 'comprobante_pago')
    
    # Filtros laterales
    list_filter = ('estado', 'metodo', 'codigo_qr__banco')
    
    # Campos de búsqueda
    search_fields = ('equipo__nombre', 'codigo_qr__banco')
    
    # Orden por defecto
    ordering = ('-fecha_pago',)



  
class SuspensionAdmin(admin.ModelAdmin):
    # Campos visibles en la lista
    list_display = ('jugador', 'fecha_inicio', 'fecha_fin', 'motivo', 'esta_activa_display')

    # Filtros para facilitar búsqueda
    list_filter = ('fecha_inicio', 'fecha_fin')

    # Campos que se pueden buscar
    search_fields = ('jugador__usuario__username', 'motivo')

    # Orden por defecto
    ordering = ('-fecha_inicio',)

    # Método para mostrar si está activa con sí/no
    def esta_activa_display(self, obj):
        return "Sí" if obj.esta_activa() else "No"
    esta_activa_display.short_description = '¿Activa?'




class EstadisticaFutbolAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'campeonato', 'partidos_jugados', 'goles', 'tarjetas_amarillas', 'tarjetas_rojas', 'puntos')
    search_fields = ('equipo__nombre', 'campeonato__nombre')
    list_filter = ('campeonato',)


class EstadisticaBasquetAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'campeonato', 'partidos_jugados', 'canastas', 'rebotes', 'asistencias', 'puntos')
    search_fields = ('equipo__nombre', 'campeonato__nombre')
    list_filter = ('campeonato',)


class EstadisticaAjedrezAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'campeonato', 'partidas_jugadas', 'partidas_ganadas', 'partidas_empatadas', 'partidas_perdidas', 'puntos')
    search_fields = ('equipo__nombre', 'campeonato__nombre')
    list_filter = ('campeonato',)


class EstadisticaEcuabolyAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'campeonato', 'sets_ganados', 'sets_perdidos', 'partidos_ganados', 'puntos')
    search_fields = ('equipo__nombre', 'campeonato__nombre')
    list_filter = ('campeonato',)


class EstadisticaPingPongAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'campeonato', 'partidos_ganados', 'partidos_perdidos', 'puntos')
    search_fields = ('equipo__nombre', 'campeonato__nombre')
    list_filter = ('campeonato',)

class EstadisticaFutbolinAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'campeonato', 'partidos_ganados', 'partidos_perdidos', 'goles', 'puntos')
    search_fields = ('equipo__nombre', 'campeonato__nombre')
    list_filter = ('campeonato',)

class EstadisticaTenisAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'campeonato', 'sets_ganados', 'sets_perdidos', 'partidos_ganados', 'puntos')
    search_fields = ('equipo__nombre', 'campeonato__nombre')
    list_filter = ('campeonato',)

class EstadisticaVideojuegosAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'campeonato', 'partidas_jugadas', 'partidas_ganadas', 'partidas_perdidas', 'puntos')
    search_fields = ('equipo__nombre', 'campeonato__nombre')
    list_filter = ('campeonato',)



class TipoCampeonatoAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la tabla del admin
    list_display = ('nombre', 'descripcion')
    # Permite buscar por nombre
    search_fields = ('nombre',)
    # Ordena por nombre alfabéticamente
    ordering = ('nombre',)


class EstadisticaJugadorFutbolAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'campeonato', 'partidos_jugados', 'goles', 'tarjetas_amarillas', 'tarjetas_rojas')
    search_fields = ('jugador__usuario__username', 'campeonato__nombre')
    list_filter = ('campeonato',)


class EstadisticaJugadorBasquetAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'campeonato', 'partidos_jugados', 'canastas', 'rebotes', 'asistencias')
    search_fields = ('jugador__usuario__username', 'campeonato__nombre')
    list_filter = ('campeonato',)

class EstadisticaJugadorAjedrezAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'campeonato', 'partidas_jugadas', 'partidas_ganadas', 'partidas_empatadas', 'partidas_perdidas')
    search_fields = ('jugador__usuario__username', 'campeonato__nombre')
    list_filter = ('campeonato',)

class EstadisticaJugadorEcuabolyAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'campeonato', 'partidos_jugados', 'sets_ganados', 'sets_perdidos')
    search_fields = ('jugador__usuario__username', 'campeonato__nombre')
    list_filter = ('campeonato',)

class EstadisticaJugadorPingPongAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'campeonato', 'partidos_jugados', 'partidos_ganados', 'partidos_perdidos')
    search_fields = ('jugador__usuario__username', 'campeonato__nombre')
    list_filter = ('campeonato',)

class EstadisticaJugadorTenisAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'campeonato', 'partidos_jugados', 'sets_ganados', 'sets_perdidos')
    search_fields = ('jugador__usuario__username', 'campeonato__nombre')
    list_filter = ('campeonato',)

class EstadisticaJugadorVideojuegosAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'campeonato', 'partidas_jugadas', 'partidas_ganadas', 'partidas_perdidas')
    search_fields = ('jugador__usuario__username', 'campeonato__nombre')
    list_filter = ('campeonato',)

class EstadisticaJugadorFutbolinAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'campeonato', 'partidos_jugados', 'partidos_ganados', 'partidos_perdidos', 'goles')
    search_fields = ('jugador__usuario__username', 'campeonato__nombre')
    list_filter = ('campeonato',)




admin.site.register(Suspension, SuspensionAdmin)
admin.site.register(Deporte, DeporteAdmin)
    # Registra el modelo Campeonato 
admin.site.register(Campeonato, CampeonatoAdmin)

# Registra el modelo Equipo para que aparezca en el panel
admin.site.register(Equipo, EquipoAdmin)
# Registra el modelo Jugador asociado a un usuario y equipo
admin.site.register(Jugador, JugadorAdmin)
# Registra el modelo Arbitro con asignación de deportes
admin.site.register(Arbitro, ArbitroAdmin)
# Registra el modelo Partido donde se definen encuentros entre equipos
admin.site.register(Partido, PartidoAdmin)

# codigo QR para el pago 
admin.site.register(CodigoQR, CodigoQRAdmin)
# Registra el modelo Transmision para gestionar las transmisiones de partidos
admin.site.register(Transmision, TransmisionAdmin)
# Registra el modelo Pago para gestionar los pagos de los usuarios
admin.site.register(Pago, PagoAdmin)
# Registra el modelo TipoCampeonato 
admin.site.register(TipoCampeonato, TipoCampeonatoAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(EstadisticaFutbol, EstadisticaFutbolAdmin)
# Registra los modelos de estadísticas para diferentes deportes
admin.site.register(EstadisticaBasquet, EstadisticaBasquetAdmin)
# Registra las estadísticas de ajedrez
admin.site.register(EstadisticaAjedrez, EstadisticaAjedrezAdmin)
# Registra las estadísticas de ecuaboly
admin.site.register(EstadisticaEcuaboly, EstadisticaEcuabolyAdmin)
# Registra las estadísticas de ping pong
admin.site.register(EstadisticaPingPong, EstadisticaPingPongAdmin)
# Registra las estadísticas de futbolín
admin.site.register(EstadisticaFutbolin, EstadisticaFutbolinAdmin)
# Registra las estadísticas de tenis
admin.site.register(EstadisticaTenis, EstadisticaTenisAdmin)
# Registra las estadísticas de videojuegos
admin.site.register(EstadisticaVideojuegos, EstadisticaVideojuegosAdmin)
# Estadísticas por jugador - Futbol
admin.site.register(EstadisticaJugadorFutbol, EstadisticaJugadorFutbolAdmin)
# Estadísticas por jugador - Basquet
admin.site.register(EstadisticaJugadorBasquet, EstadisticaJugadorBasquetAdmin)
# Estadísticas por jugador - Ecuaboly
admin.site.register(EstadisticaJugadorEcuaboly, EstadisticaJugadorEcuabolyAdmin)
# Estadísticas por jugador - Tenis
admin.site.register(EstadisticaJugadorTenis, EstadisticaJugadorTenisAdmin)
# Estadísticas por jugador - Ping Pong
admin.site.register(EstadisticaJugadorPingPong, EstadisticaJugadorPingPongAdmin)
# Estadísticas por jugador - Futbolín
admin.site.register(EstadisticaJugadorFutbolin, EstadisticaJugadorFutbolinAdmin)
# Estadísticas por jugador - Ajedrez
admin.site.register(EstadisticaJugadorAjedrez, EstadisticaJugadorAjedrezAdmin)
# Estadísticas por jugador - Videojuegos
admin.site.register(EstadisticaJugadorVideojuegos, EstadisticaJugadorVideojuegosAdmin)
admin.site.register(Carrera, CarreraAdmin)
