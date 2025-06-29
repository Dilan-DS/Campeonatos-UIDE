from django.contrib import admin  
from .models import *

# Registra el modelo Usuario para poder gestionarlo desde el panel de administración
admin.site.register(Usuario)

# Registra el modelo Deporte como Fútbol, Básquet, etc.
admin.site.register(Deporte)
# Registra el modelo Campeonato 
admin.site.register(Campeonato)
# Registra el modelo Equipo para que aparezca en el panel
admin.site.register(Equipo)
# Registra el modelo Jugador asociado a un usuario y equipo
admin.site.register(Jugador)
# Registra el modelo Arbitro con asignación de deportes
admin.site.register(Arbitro)
# Registra el modelo Partido donde se definen encuentros entre equipos
admin.site.register(Partido)
# codigo QR para el pago 
admin.site.register(CodigoQR)
# Registra el modelo Transmision para gestionar las transmisiones de partidos
admin.site.register(Transmision)
# Registra el modelo Pago para gestionar los pagos de los usuarios
admin.site.register(Pago)

admin.site.register(Suspension)  

admin.site.register(EstadisticaFutbol)

admin.site.register(EstadisticaBasquet)
admin.site.register(EstadisticaAjedrez)
admin.site.register(EstadisticaEcuaboly)
admin.site.register(EstadisticaPingPong)
admin.site.register(EstadisticaFutbolin)
admin.site.register(EstadisticaTenis)
admin.site.register(EstadisticaVideojuegos)
