"""Paginas de error orientadas al usuario final.

Con DEBUG=False (produccion) Django ya deja de mostrar el traceback tecnico,
pero sin esto cae en sus paginas por defecto: la de CSRF explica un mecanismo
de seguridad interno ("verificacion CSRF", "cookie") que a un usuario normal
no le dice nada y sin una accion clara que tomar. Aqui se reemplazan por
mensajes en espanol que explican que no se perdio nada y que hacer.

CSRF_FAILURE_VIEW (settings.py) apunta a csrf_failure. handler403/404/500
(CampeonatosUIDE/urls.py) apuntan a las otras tres.
"""
from django.shortcuts import render


def csrf_failure(request, reason=""):
    """Se dispara cuando falta o no coincide el token CSRF de un formulario.

    Motivo mas comun en este proyecto: la pestana quedo abierta mucho
    tiempo (el token asociado a la sesion expiro) o el navegador bloquea
    cookies de terceros/modo incognito estricto. No es un fallo de la
    aplicacion ni se perdieron datos: el formulario nunca llego a guardarse.
    """
    return render(request, "errores/403_csrf.html", status=403)


def error_403(request, exception=None):
    return render(request, "errores/403.html", status=403)


def error_404(request, exception=None):
    return render(request, "errores/404.html", status=404)


def error_500(request):
    return render(request, "errores/500.html", status=500)
