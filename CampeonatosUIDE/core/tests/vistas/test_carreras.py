"""CRUD de Carrera (carrera_views.py), sin ningun test propio (60% real)."""

from core.tests.base import *  # noqa: F401,F403


class ListadoDeCarreras(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_solo_el_admin_puede_ver_el_listado(self):
        self.client.force_login(self.datos["delegado"])
        respuesta = self.client.get(reverse("listar_carreras"))
        self.assertEqual(respuesta.status_code, 403)

    def test_el_admin_ve_el_listado(self):
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(reverse("listar_carreras"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(self.datos["carrera"], respuesta.context["carreras"])


class AltaDeCarrera(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def setUp(self):
        self.client.force_login(self.datos["admin"])

    def test_get_muestra_el_formulario_vacio(self):
        respuesta = self.client.get(reverse("registrar_carrera"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["modo"], "crear")

    def test_post_valido_crea_la_carrera(self):
        respuesta = self.client.post(reverse("registrar_carrera"), {"nombre": "Ingeniería Civil"})
        self.assertRedirects(respuesta, reverse("listar_carreras"))
        self.assertTrue(Carrera.objects.filter(nombre="Ingeniería Civil").exists())

    def test_post_con_nombre_duplicado_no_crea_otra(self):
        antes = Carrera.objects.count()
        respuesta = self.client.post(reverse("registrar_carrera"), {"nombre": self.datos["carrera"].nombre})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["modo"], "crear")
        self.assertEqual(Carrera.objects.count(), antes)


class DetalleEdicionYBajaDeCarrera(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def setUp(self):
        self.client.force_login(self.datos["admin"])

    def test_detalle_sin_action_muestra_modo_ver(self):
        respuesta = self.client.get(reverse("detalle_carrera", args=[self.datos["carrera"].id]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["modo"], "ver")
        self.assertEqual(respuesta.context["carrera"], self.datos["carrera"])

    def test_get_editar_precarga_el_formulario(self):
        respuesta = self.client.get(reverse("editar_carrera", args=[self.datos["carrera"].id]))
        self.assertEqual(respuesta.context["modo"], "editar")
        self.assertEqual(respuesta.context["form"].instance, self.datos["carrera"])

    def test_post_editar_actualiza_el_nombre(self):
        respuesta = self.client.post(
            reverse("editar_carrera", args=[self.datos["carrera"].id]),
            {"nombre": "Ingeniería en TI (renombrada)"})
        self.assertRedirects(respuesta, reverse("listar_carreras"))
        self.datos["carrera"].refresh_from_db()
        self.assertEqual(self.datos["carrera"].nombre, "Ingeniería en TI (renombrada)")

    def test_get_eliminar_pide_confirmacion_sin_borrar(self):
        respuesta = self.client.get(reverse("eliminar_carrera", args=[self.datos["carrera"].id]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["modo"], "eliminar")
        self.assertTrue(Carrera.objects.filter(pk=self.datos["carrera"].id).exists())

    def test_post_eliminar_la_borra(self):
        otra = Carrera.objects.create(nombre="Carrera desechable")
        respuesta = self.client.post(reverse("eliminar_carrera", args=[otra.id]))
        self.assertRedirects(respuesta, reverse("listar_carreras"))
        self.assertFalse(Carrera.objects.filter(pk=otra.id).exists())

    def test_un_delegado_no_puede_editar_ni_eliminar(self):
        self.client.force_login(self.datos["delegado"])
        self.assertEqual(
            self.client.get(reverse("editar_carrera", args=[self.datos["carrera"].id])).status_code, 403)
        self.assertEqual(
            self.client.post(reverse("eliminar_carrera", args=[self.datos["carrera"].id])).status_code, 403)
        self.assertTrue(Carrera.objects.filter(pk=self.datos["carrera"].id).exists())
