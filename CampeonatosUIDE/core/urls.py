from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import *


urlpatterns = [
    # Inicio público y dashboard general
    path('', vista_inicio_publico, name='inicio_publico'),
    path('dashboard/', vista_inicio, name='vista_inicio'),


    # Dashboards por rol
    path('panel/admin/', admin_dashboard, name='admin_dashboard'),
    path('panel/admin/crear-usuario/', crear_usuario_admin, name='crear_usuario_admin'),
    path('panel/delegado/', delegado_dashboard, name='delegado_dashboard'),
    path('panel/jugador/', jugador_dashboard, name='jugador_dashboard'),


    path('deportes/', views.listar_deportes, name='listar_deportes'),  
    path('tipos-campeonato/', listar_tipos_campeonato, name='listar_tipos_campeonato'),


    # Autenticación
    path('login/', vista_login, name='login'),
    path('logout/', vista_logout, name='logout'),
    path('registro/', vista_registro, name='registro'),
    path('perfil/', vista_perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', editar_perfil, name='editar_perfil'),

    # Recuperación de contraseña
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
    path('transmisiones/<int:id>/editar/', editar_transmision, name='editar_transmision'),
    path('transmisiones/<int:id>/eliminar/', eliminar_transmision, name='eliminar_transmision'),

    # Partidos
    path('partidos/', listar_partidos, name='listar_partidos'),
    path('partidos/registrar/', registrar_partido, name='registrar_partido'),
    path('partidos/<int:partido_id>/', detalle_partido, name='detalle_partido'),

    # Suspensiones
    path('suspensiones/', listar_suspensiones, name='listar_suspensiones'),
    path('suspension/<int:suspension_id>/', detalle_suspension, name='detalle_suspension'),
    path('suspension/registrar/', registrar_suspension, name='registrar_suspension'),



    path('deportes/', listar_deportes, name='listar_deportes'),
    path('deportes/registrar/', registrar_deporte, name='registrar_deporte'),

    path('tipos-campeonato/', listar_tipos_campeonato, name='listar_tipos_campeonato'),
    path('tipos-campeonato/registrar/', registrar_tipo_campeonato, name='registrar_tipo_campeonato'),

]
