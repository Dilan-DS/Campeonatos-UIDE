from django.urls import path
from .views import (
    vista_login,
    vista_logout,
    vista_registro,
    vista_inicio_publico,
    vista_tabla_publica,
    campeonatos_publicos, 

    # Árbitros
    listar_arbitros,
    registrar_arbitro,
    editar_arbitro,
    detalle_arbitro,

    # Campeonatos
    listar_campeonatos,
    crear_campeonato,
    editar_campeonato,
    detalle_campeonato,
    fixture_campeonato,

    # Equipos
    listar_equipos,
    registrar_equipo,
    detalle_equipo,
    editar_equipo,
    pago_equipo,
    jugadores_equipo,

    # Estadísticas por deporte
    estadisticas_futbol,
    estadisticas_basquet,
    estadisticas_ecuaboly,
    estadisticas_ajedrez,
    estadisticas_tenis,
    estadisticas_pingpong,
    estadisticas_futbolin,
    estadisticas_videojuegos,

    # Transmisiones
    listar_transmisiones,
    registrar_transmision,
    detalle_transmision,
)



urlpatterns = [
    # Página pública
    path('', vista_inicio_publico, name='inicio_publico'),
    

    # Autenticación
    path('login/', vista_login, name='login'),
    path('logout/', vista_logout, name='logout'),
    path('registro/', vista_registro, name='registro'),

    # Dashboard
#    path('admin/dashboard/', vista_dashboard, name='dashboard'),

    # Árbitros
    path('arbitros/', listar_arbitros, name='listar_arbitros'),
    path('arbitros/nuevo/', registrar_arbitro, name='registrar_arbitro'),
    path('arbitros/<int:id>/', detalle_arbitro, name='detalle_arbitro'),
    path('arbitros/<int:id>/editar/', editar_arbitro, name='editar_arbitro'),

    # Campeonatos
   # Campeonatos públicos (visibles sin iniciar sesión)
    path('campeonatos/publicos/', campeonatos_publicos, name='campeonatos_publicos'),
    path('tabla-publica/<int:campeonato_id>/', vista_tabla_publica, name='tabla_estadisticas'),

    # Campeonatos privados (administración)
    path('campeonatos/', listar_campeonatos, name='listar_campeonatos'),

    path('campeonatos/nuevo/', crear_campeonato, name='crear_campeonato'),
    path('campeonatos/<int:id>/', detalle_campeonato, name='detalle_campeonato'),
    path('campeonatos/<int:id>/editar/', editar_campeonato, name='editar_campeonato'),
    path('campeonatos/<int:id>/fixture/', fixture_campeonato, name='fixture_campeonato'),

    # Equipos
    path('equipos/', listar_equipos, name='listar_equipos'),
    path('equipo/nuevo/', registrar_equipo, name='registrar_equipo'),
    path('equipo/<int:id>/', detalle_equipo, name='detalle_equipo'),
    path('equipo/<int:id>/editar/', editar_equipo, name='editar_equipo'),
    path('equipo/<int:id>/pago/', pago_equipo, name='pago_equipo'),
    path('equipo/<int:id>/jugadores/', jugadores_equipo, name='jugadores_equipo'),

    # Estadísticas
    path('estadisticas/futbol/', estadisticas_futbol, name='estadisticas_futbol'),
    path('estadisticas/basquet/', estadisticas_basquet, name='estadisticas_basquet'),
    path('estadisticas/ecuaboly/', estadisticas_ecuaboly, name='estadisticas_ecuaboly'),
    path('estadisticas/ajedrez/', estadisticas_ajedrez, name='estadisticas_ajedrez'),
    path('estadisticas/tenis/', estadisticas_tenis, name='estadisticas_tenis'),
    path('estadisticas/pingpong/', estadisticas_pingpong, name='estadisticas_pingpong'),
    path('estadisticas/futbolin/', estadisticas_futbolin, name='estadisticas_futbolin'),
    path('estadisticas/videojuegos/', estadisticas_videojuegos, name='estadisticas_videojuegos'),

    # Transmisiones
    path('transmisiones/', listar_transmisiones, name='listar_transmisiones'),
    path('transmisiones/nuevo/', registrar_transmision, name='registrar_transmision'),
    path('transmisiones/<int:id>/', detalle_transmision, name='detalle_transmision'),
]
