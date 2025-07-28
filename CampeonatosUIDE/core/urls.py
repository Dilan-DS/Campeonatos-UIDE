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

    path('arbitros/', listar_arbitros.as_view(), name='listar_arbitros'),
    path('arbitros/nuevo/', registrar_arbitro.as_view(), name='registrar_arbitro'),
    path('arbitros/<int:id>/', detalle_arbitro.as_view(), name='detalle_arbitro'),
    path('arbitros/<int:id>/editar/', editar_arbitro.as_view(), name='editar_arbitro'),
    path('arbitros/<int:id>/eliminar/', eliminar_arbitro.as_view(), name='eliminar_arbitro'),


    path('campeonatos/publicos/', CampeonatosPublicos.as_view(), name='campeonatos_publicos'),
    # path('tabla-publica/<int:campeonato_id>/', vista_tabla_publica, name='tabla_estadisticas'),
    path('campeonatos/', ListarCampeonatos.as_view(), name='listar_campeonatos'),
    path('campeonatos/nuevo/', CrearCampeonato.as_view(), name='crear_campeonato'),
    path('campeonatos/<int:id>/', DetalleCampeonato.as_view(), name='detalle_campeonato'),
    path('campeonatos/<int:id>/editar/', EditarCampeonato.as_view(), name='editar_campeonato'),
    path('campeonatos/<int:id>/fixture/', FixtureCampeonato.as_view(), name='fixture_campeonato'),
    path('campeonatos/<int:id>/eliminar/', EliminarCampeonato.as_view(), name='eliminar_campeonato'),
 # Rutas de deportes
    path('deportes/', ListarDeportesView.as_view(), name='listar_deportes'),
    path('deportes/registrar/', RegistrarDeporteView.as_view(), name='registrar_deporte'),
    path('deportes/<int:id>/editar/', EditarDeporteView.as_view(), name='editar_deporte'),
    path('deportes/<int:id>/eliminar/', EliminarDeporteView.as_view(), name='eliminar_deporte'),

    # Rutas de tipos de campeonato
    path('tipos-campeonato/', ListaTiposCampeonatoView.as_view(), name='listar_tipos_campeonato'),
    path('tipos-campeonato/registrar/', RegistrarTipoCampeonatoView.as_view(), name='registrar_tipo_campeonato'),
    path('tipos-campeonato/<int:id>/editar/', EditarTipoCampeonatoView.as_view(), name='editar_tipo_campeonato'),
    path('tipos-campeonato/<int:id>/eliminar/', EliminarTipoCampeonatoView.as_view(), name='eliminar_tipo_campeonato'),

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
    path('transmisiones/', ListarTransmisionView.as_view(), name='listar_transmisiones'),
    path('transmisiones/crear/', CrearTransmisionView.as_view(), name='crear_transmision'),
    path('transmisiones/<int:id>/', DetalleTransmisionView.as_view(), name='detalle_transmision'),
    path('transmisiones/<int:id>/editar/', EditarTransmisionView.as_view(), name='editar_transmision'),
    path('transmisiones/<int:id>/eliminar/', EliminarTransmisionView.as_view(), name='eliminar_transmision'),
    # Suspensiones
    path('suspensiones/', listar_suspensiones, name='listar_suspensiones'),
    path('suspension/registrar/', registrar_suspension, name='registrar_suspension'),
    path('suspension/<int:suspension_id>/', detalle_suspension, name='detalle_suspension'),

    # Códigos QR
    path('panel/admin/codigos-qr/', ListarCodigosQRView.as_view(), name='listar_codigos_qr'),
    path('panel/admin/codigos-qr/registrar/', RegistrarCodigoQRView.as_view(), name='registrar_codigo_qr'),
    path('panel/admin/codigos-qr/<int:pk>/editar/', EditarCodigoQRView.as_view(), name='editar_codigo_qr'),
    path('panel/admin/codigos-qr/<int:pk>/', DetalleCodigoQRView.as_view(), name='detalle_codigo_qr'),
    path('panel/admin/codigos-qr/<int:pk>/eliminar/', EliminarCodigoQRView.as_view(), name='eliminar_codigo_qr'),

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