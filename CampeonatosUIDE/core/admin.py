from django.contrib import admin  
from .models import *

# Registra el modelo Usuario para poder gestionarlo desde el panel de administración
admin.site.register(Usuario)

# Registra el modelo Deporte como Fútbol, Básquet, etc.
admin.site.register(Deporte)

# Registra el modelo Campeonato para crear/editar campeonatos desde el admin
admin.site.register(Campeonato)

# Registra el modelo Equipo para que aparezca en el panel
admin.site.register(Equipo)

# Registra el modelo Jugador asociado a un usuario y equipo
admin.site.register(Jugador)

# Registra el modelo Arbitro con asignación de deportes
admin.site.register(Arbitro)

# Registra el modelo Partido donde se definen encuentros entre equipos
admin.site.register(Partido)

# Registra el modelo Estadística datos acumulados por equipo
admin.site.register(EstadisticasCampeonato)
