"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class TestimoniosExigenSesion(PruebaBase):
    """Registrar/Editar/EliminarTestimonio eran `View` sin comprobacion.

    Comprobado antes del arreglo: un cliente sin sesion creaba, editaba y
    borraba testimonios.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_un_anonimo_no_puede_crear(self):
        antes = Testimonio.objects.count()
        self.client.post(reverse("registrar_testimonio"),
                         {"autor": "Atacante", "contenido": "Sin sesion."})
        self.assertEqual(Testimonio.objects.count(), antes,
                         "un anonimo no debe poder crear testimonios")

    def test_un_anonimo_no_puede_editar_ni_borrar(self):
        testimonio = Testimonio.objects.first()
        autor = testimonio.autor
        self.client.post(reverse("editar_testimonio", args=[testimonio.id]),
                         {"autor": "Modificado", "contenido": "x"})
        testimonio.refresh_from_db()
        self.assertEqual(testimonio.autor, autor, "no debe poder editarlo")

        self.client.post(reverse("eliminar_testimonio", args=[testimonio.id]))
        self.assertTrue(Testimonio.objects.filter(id=testimonio.id).exists(),
                        "no debe poder borrarlo")

    def test_un_jugador_tampoco(self):
        self.client.force_login(self.datos["jugador"].usuario)
        antes = Testimonio.objects.count()
        self.client.post(reverse("registrar_testimonio"),
                         {"autor": "Jugador", "contenido": "x"})
        self.assertEqual(Testimonio.objects.count(), antes)

    def test_el_admin_si_puede(self):
        """El arreglo no debe dejar fuera a quien si gestiona testimonios."""
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(reverse("registrar_testimonio"))
        self.assertEqual(respuesta.status_code, 200)

    def test_el_listado_sigue_siendo_publico(self):
        self.assertEqual(self.client.get(reverse("listar_testimonios")).status_code, 200)


class SuspensionesNoSonPublicas(PruebaBase):
    """El expediente disciplinario llevaba nombre y motivo, y era publico."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_un_anonimo_no_ve_el_listado(self):
        respuesta = self.client.get(reverse("listar_suspensiones"))
        self.assertEqual(respuesta.status_code, 302,
                         "debe redirigir al login, no responder 200")

    def test_un_anonimo_no_ve_el_detalle(self):
        suspension = Suspension.objects.first()
        respuesta = self.client.get(reverse("detalle_suspension", args=[suspension.id]))
        self.assertEqual(respuesta.status_code, 302)

    def test_el_admin_sigue_viendo_todo(self):
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(reverse("listar_suspensiones"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.context["suspensiones"]), Suspension.objects.count())

    def test_un_jugador_solo_ve_la_suya(self):
        otro = Usuario.objects.create_user(
            username="jugador_sin_sancion", email="jsn@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="masculino")
        Jugador.objects.create(usuario=otro, equipo=self.datos["equipo"],
                               numero_camiseta=11, posicion="Defensa", edad=20)
        self.client.force_login(otro)
        respuesta = self.client.get(reverse("listar_suspensiones"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(list(respuesta.context["suspensiones"]), [],
                         "no debe ver expedientes de otros jugadores")

    def test_pedir_un_expediente_ajeno_da_404(self):
        otro = Usuario.objects.create_user(
            username="jugador_curioso", email="jc@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="masculino")
        Jugador.objects.create(usuario=otro, equipo=self.datos["equipo"],
                               numero_camiseta=12, posicion="Portero", edad=22)
        self.client.force_login(otro)
        suspension = Suspension.objects.first()
        respuesta = self.client.get(reverse("detalle_suspension", args=[suspension.id]))
        self.assertEqual(respuesta.status_code, 404,
                         "404 y no 403: no debe confirmar que el expediente existe")

