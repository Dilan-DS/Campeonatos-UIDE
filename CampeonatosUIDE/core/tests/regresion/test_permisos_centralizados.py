"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class PermisosEnUnSoloSitio(PruebaBase):
    """es_admin estaba en cinco modulos y es_admin_o_delegado en otros cinco.

    No eran copias identicas: cuatro de los cinco es_admin hacian
    `user.rol == 'ADMIN'`, que lanza AttributeError con un usuario anonimo
    porque AnonymousUser no tiene `rol`. Solo no se notaba donde hubiera un
    @login_required por delante. Ahora hay una unica version, la segura.
    """

    def test_ningun_modulo_de_vistas_los_redefine(self):
        repetidos = []
        for nombre_modulo, modulo in _modulos_de_vistas():
            definidos = _definidos_en(modulo)
            for funcion in ("es_admin", "es_admin_o_delegado"):
                if funcion in definidos:
                    repetidos.append(f"{funcion} en {nombre_modulo}")
        self.assertEqual(repetidos, [],
                         "deben importarse de core.permisos: " + ", ".join(repetidos))

    def test_no_revientan_con_un_usuario_anonimo(self):
        """Es la diferencia entre un 500 y una redireccion al login."""
        from django.contrib.auth.models import AnonymousUser
        from core.permisos import es_admin, es_admin_o_delegado

        anonimo = AnonymousUser()
        self.assertFalse(es_admin(anonimo))
        self.assertFalse(es_admin_o_delegado(anonimo))
        self.assertFalse(es_admin(None))
        self.assertFalse(es_admin_o_delegado(None))

    def test_responden_bien_por_rol(self):
        from core.permisos import es_admin, es_admin_o_delegado

        datos = _datos_base()
        casos = {
            "admin": (datos["admin"], True, True),
            "delegado": (datos["delegado"], False, True),
            "arbitro": (datos["arbitro"].usuario, False, False),
            "jugador": (datos["jugador"].usuario, False, False),
        }
        for etiqueta, (usuario, admin, admin_o_delegado) in casos.items():
            with self.subTest(rol=etiqueta):
                self.assertIs(es_admin(usuario), admin)
                self.assertIs(es_admin_o_delegado(usuario), admin_o_delegado)

    def test_un_rol_desconocido_no_da_permisos(self):
        from core.permisos import es_admin, es_admin_o_delegado

        class Raro:
            is_authenticated = True
            rol = "INVENTADO"

        self.assertFalse(es_admin(Raro()))
        self.assertFalse(es_admin_o_delegado(Raro()))

    def test_un_usuario_sin_atributo_rol_no_da_permisos(self):
        from core.permisos import es_admin

        class SinRol:
            is_authenticated = True

        self.assertFalse(es_admin(SinRol()))

