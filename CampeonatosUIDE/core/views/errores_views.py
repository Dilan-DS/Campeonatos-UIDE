"""Paginas de error orientadas al usuario final.

Una sola plantilla generica (errores/generico.html) para 403/404/500/CSRF,
en vez de un archivo por codigo: cambia el titulo/mensaje, no el diseno.
Se ve como un modal corto (tarjeta centrada), no una pagina distinta por
cada tipo de fallo.

CSRF_FAILURE_VIEW (settings.py) apunta a csrf_failure. handler403/404/500
(CampeonatosUIDE/urls.py) apuntan a las otras tres.
"""
from django.shortcuts import render


def _pagina_error(request, status, titulo, mensaje):
    return render(request, "errores/generico.html", {"titulo": titulo, "mensaje": mensaje}, status=status)


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
    return _pagina_error(request, 500, "Algo falló de nuestro lado", "Ya quedó registrado, intenta de nuevo en unos minutos.")
