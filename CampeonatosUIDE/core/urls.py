
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    editar_perfil,
    vista_perfil_usuario,
    vista_inicio,
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

    # Partidos
    listar_partidos,
    registrar_partido,
    detalle_partido,

    # Suspensiones
    listar_suspensiones,
    registrar_suspension,
    detalle_suspension,

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
    # Página de inicio pública
    path('', vista_inicio_publico, name='inicio_publico'),

    # Dashboard (vista protegida después de login)
    path('dashboard/', vista_inicio, name='dashboard'),


    # Autenticación
    path('login/', vista_login, name='login'),
    path('logout/', vista_logout, name='logout'),
    path('registro/', vista_registro, name='registro'),
    path('perfil/', vista_perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', editar_perfil, name='editar_perfil'), 

     # Vista de recuperación de contraseña
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='usuario/password_reset.html'), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='usuario/password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='usuario/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='usuario/password_reset_complete.html'), name='password_reset_complete'),
    # Árbitros
    path('arbitros/', listar_arbitros, name='listar_arbitros'),
    path('arbitros/nuevo/', registrar_arbitro, name='registrar_arbitro'),
    path('arbitros/<int:id>/', detalle_arbitro, name='detalle_arbitro'),
    path('arbitros/<int:id>/editar/', editar_arbitro, name='editar_arbitro'),

    # Campeonatos
    path('campeonatos/publicos/', campeonatos_publicos, name='campeonatos_publicos'),
    path('tabla-publica/<int:campeonato_id>/', vista_tabla_publica, name='tabla_estadisticas'),
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

    # Partidos
    path('partidos/', listar_partidos, name='listar_partidos'),
    path('partidos/registrar/', registrar_partido, name='registrar_partido'),
    path('partidos/<int:partido_id>/', detalle_partido, name='detalle_partido'),

    #suspendidos
    path('suspensiones/', listar_suspensiones, name='listar_suspensiones'),
    path('suspension/<int:suspension_id>/', detalle_suspension, name='detalle_suspension'),
    path('suspension/registrar/', registrar_suspension, name='registrar_suspension'),
]
