from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *
from .views.carrera_views import ListarCarrerasView, GestionCarreraView
from .views.partido_views import listar_partidos, fixture_campeonato_view, calendario_global_view
from .views.feachure_views import calendar_view
from .views.arbitro_views import listar_arbitros, ver_tabla_posiciones_arbitro
from core.views.inicio_views import equipo_publico
from core.views.admin_views import exportar_estadisticas_pdf, exportar_estadisticas_excel
from django.conf import settings
from django.conf.urls.static import static
from .views import transmision_views
from core.forms import PasswordResetConValidacionForm
from .views.auth_extra import PasswordResetViewWithEcho, PasswordResetDoneViewWithEcho

urlpatterns = [
    # Inicio público y dashboard general
    path('', vista_inicio_publico, name='inicio_publico'),
    path("equipo/", equipo_publico, name="equipo_publico"),
    path('dashboard/', vista_inicio, name='vista_inicio'),

    # Dashboards por rol
    path('panel/admin/', admin_dashboard, name='admin_dashboard'),
    path('panel/admin/crear-usuario/', crear_usuario_admin, name='crear_usuario_admin'),

    # Delegados
    path('delegados/', ListarDelegadosView.as_view(), name='listar_delegados'),
    path('delegados/registrar/', RegistrarDelegadoAdminView.as_view(), name='registrar_delegado'),
    path('panel/delegado/', DelegadoDashboardView.as_view(), name='delegado_dashboard'),
    path('delegado/jugadores/', ListarJugadoresParaEquipoView.as_view(), name='listar_jugadores_para_equipo'),
    path('delegado/jugadores/agregar/<int:jugador_usuario_id>/', AgregarJugadorAEquipoView.as_view(), name='agregar_jugador_a_equipo'),
    path('panel/jugador/', jugador_dashboard, name='jugador_dashboard'),
    path('jugador/estadisticas/<int:jugador_id>/', ver_estadisticas_jugador, name='ver_estadisticas_jugador'),
    path('jugador/mis-partidos/', ver_mis_partidos, name='ver_mis_partidos'),
    path('jugador/registrar/', registrar_jugador, name='registrar_jugador'),
    path('jugador/completar-perfil/', completar_perfil_jugador, name='completar_perfil_jugador'),
    path('equipo/<int:id>/detalle/', detalle_equipo, name='detalle_equipo'),

    # Autenticación y perfil
    path('login/', vista_login, name='login'),
    path('logout/', vista_logout, name='logout'),
    path('registro/', vista_registro, name='registro'),
    path('perfil/', vista_perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', editar_perfil, name='editar_perfil'),

    # Recuperación de contraseña
    path(
        'reset_password/',
        PasswordResetViewWithEcho.as_view(
            template_name='usuario/password_reset.html',
            email_template_name='usuario/email/password_reset_email.txt',
            html_email_template_name='usuario/email/password_reset_email.html',  # usar HTML
            subject_template_name='usuario/email/password_reset_subject.txt',
            from_email=settings.DEFAULT_FROM_EMAIL,
            form_class=PasswordResetConValidacionForm,
        ),
        name='password_reset',
    ),
    path('reset_password_sent/', PasswordResetDoneViewWithEcho.as_view(template_name='usuario/password_reset_sent.html'), name='password_reset_done', ),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='usuario/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='usuario/password_reset_complete.html'), name='password_reset_complete'),

    path('arbitros/', listar_arbitros, name='listar_arbitros'),
    path('arbitros/registrar/', GestionArbitroView.as_view(), name='registrar_arbitro'),
    path('arbitros/<int:id>/', GestionArbitroView.as_view(), name='detalle_arbitro'),
    path('arbitros/<int:id>/editar/', GestionArbitroView.as_view(), {'action': 'editar'}, name='editar_arbitro'),
    path('arbitros/<int:id>/eliminar/', GestionArbitroView.as_view(), {'action': 'eliminar'}, name='eliminar_arbitro'),
    path('arbitro/mis-partidos/', mis_partidos_arbitro, name='mis_partidos_arbitro'),
    path('arbitro/historial/', historial_arbitros, name='historial_arbitros'),
    path('arbitro/campeonato/<int:campeonato_id>/posiciones/', ver_tabla_posiciones_arbitro, name='ver_tabla_posiciones_arbitro'),
    path('arbitro/partido/<int:pk>/acta/', acta_partido_arbitro, name='acta_partido_arbitro'), # New path added
    # NUEVOS ALIAS para compatibilidad con el template:
    path('arbitro/partido/<int:pk>/registrar-resultado/', acta_partido_arbitro, name='registrar_resultado_partido'),
    path('arbitro/partido/<int:pk>/disciplinario/', acta_partido_arbitro, name='disciplinario_partido'),


    path('campeonatos/publicos/', CampeonatosPublicos.as_view(), name='campeonatos_publicos'),
    path('resultados-publicos/', resultados_publicos, name='resultados_publicos'),
    # path('tabla-publica/<int:campeonato_id>/', vista_tabla_publica, name='tabla_estadisticas'),
    path('campeonatos/', ListarCampeonatos.as_view(), name='listar_campeonatos'),
    path('campeonatos/nuevo/', CrearCampeonato.as_view(), name='crear_campeonato'),
    path('campeonatos/<int:id>/', DetalleCampeonato.as_view(), name='detalle_campeonato'),
    path('campeonatos/<int:id>/editar/', EditarCampeonato.as_view(), name='editar_campeonato'),
    path('campeonatos/<int:id>/fixture/', FixtureCampeonato.as_view(), name='fixture_campeonato'),
    path('campeonatos/<int:campeonato_id>/fixture-detalle/', fixture_campeonato_view, name='fixture_campeonato_detalle'),
    path('campeonatos/<int:id>/eliminar/', EliminarCampeonato.as_view(), name='eliminar_campeonato'),
    path('campeonatos/<int:campeonato_id>/tabla-posiciones/', TablaPosiciones.as_view(), name='tabla_posiciones'),
    path('campeonatos/<int:campeonato_id>/generar-fixture/', GenerarFixtureCampeonato.as_view(), name='generar_fixture_campeonato'),
    path('campeonatos/<int:campeonato_id>/tabla-posiciones/exportar/pdf/', export_tabla_posiciones_pdf, name='export_tabla_posiciones_pdf'),
    path('campeonatos/<int:campeonato_id>/tabla-posiciones/exportar/excel/', export_tabla_posiciones_excel, name='export_tabla_posiciones_excel'),
 # Rutas de deportes
    path('deportes/', ListarDeportesView.as_view(), name='listar_deportes'),
    path('deportes/registrar/', RegistrarDeporteView.as_view(), name='registrar_deporte'),
    path('deportes/<int:id>/editar/', EditarDeporteView.as_view(), name='editar_deporte'),
    path('deportes/<int:id>/eliminar/', EliminarDeporteView.as_view(), name='eliminar_deporte'),

    
    

    # Equipos
    path('equipos/', listar_equipos, name='listar_equipos'),
    path('equipo/nuevo/', registrar_equipo, name='registrar_equipo'),
    path('equipo/<int:id>/', detalle_equipo, name='detalle_equipo'),
    path('equipo/<int:id>/editar/', editar_equipo, name='editar_equipo'),
    path('equipo/<int:id>/pago/', pago_equipo, name='pago_equipo'),
    path('equipo/<int:id>/jugadores/', jugadores_equipo, name='jugadores_equipo'),
    path('delegado/mis-jugadores/', mis_jugadores_delegado, name='mis_jugadores_delegado'),
    path('equipo/<int:equipo_id>/mi-equipo/', ver_equipo_jugador, name='ver_equipo_jugador'),
    path('equipo/<int:id>/eliminar/', eliminar_equipo, name='eliminar_equipo'),

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
    path('mis-estadisticas/', mis_estadisticas, name='mis_estadisticas'),
    path('estadisticas/futbol/exportar/pdf/', export_estadisticas_futbol_pdf, name='export_estadisticas_futbol_pdf'),
    path('estadisticas/futbol/exportar/excel/', export_estadisticas_futbol_excel, name='export_estadisticas_futbol_excel'),
    path('estadisticas/basquet/exportar/pdf/', export_estadisticas_basquet_pdf, name='export_estadisticas_basquet_pdf'),
    path('estadisticas/basquet/exportar/excel/', export_estadisticas_basquet_excel, name='export_estadisticas_basquet_excel'),
    path('estadisticas/ajedrez/exportar/pdf/', export_estadisticas_ajedrez_pdf, name='export_estadisticas_ajedrez_pdf'),
    path('estadisticas/ajedrez/exportar/excel/', export_estadisticas_ajedrez_excel, name='export_estadisticas_ajedrez_excel'),
    path('estadisticas/ecuaboly/exportar/pdf/', export_estadisticas_ecuaboly_pdf, name='export_estadisticas_ecuaboly_pdf'),
    path('estadisticas/ecuaboly/exportar/excel/', export_estadisticas_ecuaboly_excel, name='export_estadisticas_ecuaboly_excel'),
    path('estadisticas/futbolin/exportar/pdf/', export_estadisticas_futbolin_pdf, name='export_estadisticas_futbolin_pdf'),
    path('estadisticas/futbolin/exportar/excel/', export_estadisticas_futbolin_excel, name='export_estadisticas_futbolin_excel'),
    path('estadisticas/pingpong/exportar/pdf/', export_estadisticas_pingpong_pdf, name='export_estadisticas_pingpong_pdf'),
    path('estadisticas/pingpong/exportar/excel/', export_estadisticas_pingpong_excel, name='export_estadisticas_pingpong_excel'),
    path('estadisticas/tenis/exportar/pdf/', export_estadisticas_tenis_pdf, name='export_estadisticas_tenis_pdf'),
    path('estadisticas/tenis/exportar/excel/', export_estadisticas_tenis_excel, name='export_estadisticas_tenis_excel'),
    path('estadisticas/videojuegos/exportar/pdf/', export_estadisticas_videojuegos_pdf, name='export_estadisticas_videojuegos_pdf'),
    path('estadisticas/videojuegos/exportar/excel/', export_estadisticas_videojuegos_excel, name='export_estadisticas_videojuegos_excel'),

    path('estadisticas/tabla-posiciones/<int:campeonato_id>/', tabla_estadisticas, name='tabla_estadisticas'),

    # Transmisiones
    path('transmisiones/', ListarTransmisionView.as_view(), name='listar_transmisiones'),
    path('transmisiones/registrar/', transmision_views.upsert_transmision, name='registrar_transmision'),
    path('transmisiones/<int:pk>/editar/', transmision_views.upsert_transmision, name='editar_transmision'),
    path('transmisiones/<int:pk>/eliminar/', transmision_views.eliminar_transmision, name='eliminar_transmision'),
    path('transmisiones/<int:id>/', DetalleTransmisionView.as_view(), name='detalle_transmision'),
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

    path('panel/admin/registrar-delegado/', RegistrarDelegadoAdminView.as_view(), name='registrar_delegado'),
    path('panel/admin/usuarios/', listar_usuarios, name='listar_usuarios'),
    path('panel/admin/usuarios/<int:usuario_id>/editar/', editar_usuario, name='editar_usuario'),
    path('panel/admin/usuarios/<int:usuario_id>/eliminar/', eliminar_usuario, name='eliminar_usuario'),
    path('panel/admin/jugadores/', ListarJugadoresAdminView.as_view(), name='listar_jugadores_admin'),

    path('admin/exportar/pdf/', exportar_estadisticas_pdf, name='exportar_estadisticas_pdf'),
    path('admin/exportar/excel/', exportar_estadisticas_excel, name='exportar_estadisticas_excel'),


    path('partidos/generar/<int:campeonato_id>/', generar_calendario, name='generar_calendario'),
    path('partidos/calendario/', calendario_global_view, name='calendario_global'),
    # Pagos Admin
    path('panel/admin/pagos/', pago_views.ListarPagosAdminView.as_view(), name='listar_pagos_admin'),
    path('panel/admin/pagos/registrar/', pago_views.RegistrarPagoAdminView.as_view(), name='registrar_pago_admin'),
    path('panel/admin/pagos/<int:pk>/editar/', pago_views.EditarPagoAdminView.as_view(), name='editar_pago_admin'),
    path('panel/admin/pagos/<int:pk>/eliminar/', pago_views.EliminarPagoAdminView.as_view(), name='eliminar_pago_admin'),
    path('panel/admin/pagos/<int:pk>/', pago_views.DetallePagoAdminView.as_view(), name='detalle_pago_admin'),
    path('panel/admin/pagos/<int:pk>/aprobar/', pago_views.AprobarPagoAdminView.as_view(), name='aprobar_pago_admin'),
    path('panel/admin/pagos/<int:pk>/rechazar/', pago_views.RechazarPagoAdminView.as_view(), name='rechazar_pago_admin'),
    path('panel/admin/pagos/<int:pk>/estado/', pago_views.CambiarEstadoPagoAdminView.as_view(), name='cambiar_estado_pago_admin'),

    # Pagos Delegado
    path('delegado/pagos/registrar/', pago_views.RegistrarPagoDelegadoView.as_view(), name='registrar_pago_delegado'),
    path('delegado/pagos/detalle/', pago_views.DetallePagoDelegadoView.as_view(), name='detalle_pago_delegado'),
    path('delegado/pagos/<int:pk>/eliminar/', pago_views.EliminarPagoDelegadoView.as_view(), name='eliminar_pago_delegado'),

    # URLs para ImagenGaleria
    path('galeria/', ListarImagenGaleria.as_view(), name='listar_imagenes_galeria'),
    path('galeria/crear/', RegistrarImagenGaleria.as_view(), name='registrar_imagen_galeria'),
    path('galeria/editar/<int:id>/', EditarImagenGaleria.as_view(), name='editar_imagen_galeria'),
    path('galeria/eliminar/<int:id>/', EliminarImagenGaleria.as_view(), name='eliminar_imagen_galeria'),

    # URLs para Noticias
    path('noticias/', ListarNoticias.as_view(), name='listar_noticias'),
    path('noticias/crear/', RegistrarNoticia.as_view(), name='registrar_noticia'),
    path('noticias/editar/<int:id>/', EditarNoticia.as_view(), name='editar_noticia'),
    path('noticias/eliminar/<int:id>/', EliminarNoticia.as_view(), name='eliminar_noticia'),

    # URLs para Testimonios
    path('testimonios/', ListarTestimonios.as_view(), name='listar_testimonios'),
    path('testimonios/crear/', RegistrarTestimonio.as_view(), name='registrar_testimonio'),
    path('testimonios/editar/<int:id>/', EditarTestimonio.as_view(), name='editar_testimonio'),
    path('testimonios/eliminar/<int:id>/', EliminarTestimonio.as_view(), name='eliminar_testimonio'),

    # URLs para Carreras
    path('carreras/', ListarCarrerasView.as_view(), name='listar_carreras'),
    path('carreras/registrar/', GestionCarreraView.as_view(), name='registrar_carrera'),
    path('carreras/<int:id>/', GestionCarreraView.as_view(), name='detalle_carrera'),
    path('carreras/<int:id>/editar/', GestionCarreraView.as_view(), {'action': 'editar'}, name='editar_carrera'),
    path('carreras/<int:id>/eliminar/', GestionCarreraView.as_view(), {'action': 'eliminar'}, name='eliminar_carrera'),


    path('equipos/eliminar/<int:equipo_id>/', eliminar_equipo, name='eliminar_equipo'),
    path('equipos/registrar/', equipo_views.registrar_equipo, name='registrar_equipo'),
    path('campeonatos/<int:campeonato_id>/calendario/', calendar_view, name='calendario_campeonato'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)