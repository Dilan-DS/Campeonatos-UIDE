from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Inicio público y dashboard general
    path('', vista_inicio_publico, name='inicio_publico'),
    path('dashboard/', vista_inicio, name='vista_inicio'),

    # Dashboards por rol
    path('panel/admin/', admin_dashboard, name='admin_dashboard'),
    path('panel/admin/crear-usuario/', crear_usuario_admin, name='crear_usuario_admin'),
    path('panel/delegado/', delegado_dashboard, name='delegado_dashboard'),
    path('panel/jugador/', jugador_dashboard, name='jugador_dashboard'),

    # Autenticación y perfil
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
    # path('tabla-publica/<int:campeonato_id>/', vista_tabla_publica, name='tabla_estadisticas'),
    path('campeonatos/', listar_campeonatos, name='listar_campeonatos'),
    path('campeonatos/nuevo/', crear_campeonato, name='crear_campeonato'),
    path('campeonatos/<int:id>/', detalle_campeonato, name='detalle_campeonato'),
    path('campeonatos/<int:id>/editar/', editar_campeonato, name='editar_campeonato'),
    path('campeonatos/<int:id>/fixture/', fixture_campeonato, name='fixture_campeonato'),

    # Tipos de campeonato y deportes
    path('tipos-campeonato/', listar_tipos_campeonato, name='listar_tipos_campeonato'),
    path('tipos-campeonato/registrar/', registrar_tipo_campeonato, name='registrar_tipo_campeonato'),
    path('tipos-campeonato/<int:id>/editar/', editar_tipo_campeonato, name='editar_tipo_campeonato'),
    path('tipos-campeonato/<int:id>/eliminar/', eliminar_tipo_campeonato, name='eliminar_tipo_campeonato'),

    path('deportes/', listar_deportes, name='listar_deportes'),
    path('deportes/registrar/', registrar_deporte, name='registrar_deporte'),
    path('deportes/<int:id>/editar/', editar_deporte, name='editar_deporte'),
    path('deportes/<int:id>/eliminar/', eliminar_deporte, name='eliminar_deporte'),

    # Equipos
    path('equipos/', listar_equipos, name='listar_equipos'),
    path('equipo/nuevo/', registrar_equipo, name='registrar_equipo'),
    path('equipo/<int:id>/', detalle_equipo, name='detalle_equipo'),
    path('equipo/<int:id>/editar/', editar_equipo, name='editar_equipo'),
    path('equipo/<int:id>/pago/', pago_equipo, name='pago_equipo'),
    path('equipo/<int:id>/jugadores/', jugadores_equipo, name='jugadores_equipo'),

    # Partidos
    path('partidos/', listar_partidos, name='listar_partidos'),
    path('partidos/registrar/', registrar_partido, name='registrar_partido'),
    path('partidos/<int:partido_id>/', detalle_partido, name='detalle_partido'),

    # Estadísticas por deporte
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

    # Suspensiones
    path('suspensiones/', listar_suspensiones, name='listar_suspensiones'),
    path('suspension/registrar/', registrar_suspension, name='registrar_suspension'),
    path('suspension/<int:suspension_id>/', detalle_suspension, name='detalle_suspension'),

    # Códigos QR
    path('panel/admin/codigos-qr/', listar_codigos_qr, name='listar_codigos_qr'),
    path('panel/admin/codigos-qr/registrar/', registrar_codigo_qr, name='registrar_codigo_qr'),
    path('panel/admin/codigos-qr/<int:pk>/editar/', editar_codigo_qr, name='editar_codigo_qr'),
    path('panel/admin/codigos-qr/<int:pk>/eliminar/', eliminar_codigo_qr, name='eliminar_codigo_qr'),


    path('panel/admin/registrar-delegado/', registrar_delegado, name='registrar_delegado'),
    path('panel/admin/usuarios/', listar_usuarios, name='listar_usuarios'),
    path('panel/admin/usuarios/<int:usuario_id>/editar/', editar_usuario, name='editar_usuario'),
    path('panel/admin/usuarios/<int:usuario_id>/eliminar/', eliminar_usuario, name='eliminar_usuario'),


    path('partidos/generar/<int:campeonato_id>/', generar_calendario, name='generar_calendario'),
    path('partidos/calendario/', ver_calendario_completo, name='ver_calendario_completo'),
    path('jugador/mis-partidos/', ver_mis_partidos, name='ver_mis_partidos'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)