"""Paginas de error orientadas al usuario final.

Dos plantillas, no una por codigo:
- errores/generico.html: para 403/404/CSRF. Extiende comun/base.html, asi
  que se ve como el resto de la app (navbar, logo, pie), no una pantalla
  en blanco aparte.
- errores/generico_500.html: standalone, sin navbar ni context processors
  (que consultan la base de datos). Si el 500 es justo porque la base de
  datos no responde, no queremos que la propia pagina de error se caiga
  al intentar dibujar el menu.

CSRF_FAILURE_VIEW (settings.py) apunta a csrf_failure. handler403/404/500
(CampeonatosUIDE/urls.py) apuntan a las otras tres.
"""
from django.shortcuts import render


def _pagina_error(request, status, titulo, mensaje, template="errores/generico.html"):
    return render(request, template, {"titulo": titulo, "mensaje": mensaje}, status=status)


def csrf_failure(request, reason=""):
    # Causa mas comun: la pestana quedo abierta mucho tiempo (token
    # caducado) o el navegador bloquea la cookie. No se perdio nada.
    return _pagina_error(
        request, 403,
        "No se pudo enviar el formulario",
        "Recarga la página e inténtalo de nuevo. No se guardó ningún dato.",
    )


def error_403(request, exception=None):
    return _pagina_error(request, 403, "No tienes acceso", "Tu usuario no tiene permiso para ver esto.")


def error_404(request, exception=None):
    return _pagina_error(request, 404, "Página no encontrada", "El enlace está roto o la página se movió.")


def error_500(request):
    return _pagina_error(
        request, 500,
        "Algo falló de nuestro lado",
        "Ya quedó registrado, intenta de nuevo en unos minutos.",
        template="errores/generico_500.html",
    )
