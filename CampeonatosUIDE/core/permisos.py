"""Comprobaciones de rol, en un solo sitio.

Estas funciones estaban repetidas por los modulos de vistas: `es_admin` en
cinco y `es_admin_o_delegado` en otros cinco. No eran copias identicas, y
ahi estaba el problema:

    # cuatro de los cinco es_admin
    return user.rol == 'ADMIN'

    # el de arbitro_views
    return user.is_authenticated and getattr(user, "rol", "") == "ADMIN"

La primera forma revienta con AttributeError si el usuario es anonimo,
porque AnonymousUser no tiene `rol`. Solo no se notaba donde hubiera un
@login_required por delante que cortara antes. La segunda devuelve False y
deja que Django redirija al login, que es lo que se espera.

Se conserva la forma segura para las dos, asi que la comprobacion ya no
depende de que alguien se acuerde de poner el decorador correcto.
"""

ROL_ADMIN = "ADMIN"
ROL_DELEGADO = "DELEGADO"


def rol_de(user):
    """Rol del usuario, o cadena vacia si no hay usuario o no tiene rol.

    Nunca lanza: un AnonymousUser no tiene `rol`, y pedirselo directamente
    es lo que provocaba el AttributeError.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return ""
    return getattr(user, "rol", "") or ""


def es_admin(user):
    return rol_de(user) == ROL_ADMIN


def es_admin_o_delegado(user):
    return rol_de(user) in (ROL_ADMIN, ROL_DELEGADO)
