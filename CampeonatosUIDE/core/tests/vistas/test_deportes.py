"""CRUD de Deporte (deportes_views.py), sin ningun test propio (62% real)."""

from core.tests.base import *  # noqa: F401,F403


class ListadoYPermisosDeDeportes(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_solo_el_admin_ve_el_listado(self):
        """user_passes_test redirige a login en vez de devolver 403."""
        self.client.force_login(self.datos["delegado"])
        self.assertEqual(self.client.get(reverse("listar_deportes")).status_code, 302)

    def test_el_admin_ve_el_listado(self):
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(reverse("listar_deportes"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(self.datos["deporte"], respuesta.context["deportes"])

    def test_un_anonimo_no_puede_ver_el_listado(self):
        self.assertEqual(self.client.get(reverse("listar_deportes")).status_code, 302)


class AltaDeDeporte(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def setUp(self):
        self.client.force_login(self.datos["admin"])

    def test_post_valido_crea_el_deporte(self):
        respuesta = self.client.post(
            reverse("registrar_deporte"), {"nombre": "Voleibol", "descripcion": "Voley 6x6."})
        self.assertRedirects(respuesta, reverse("listar_deportes"))
        self.assertTrue(Deporte.objects.filter(nombre="Voleibol").exists())

    def test_post_con_nombre_duplicado_no_crea_otro(self):
        antes = Deporte.objects.count()
        respuesta = self.client.post(
            reverse("registrar_deporte"), {"nombre": self.datos["deporte"].nombre})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Deporte.objects.count(), antes)


class EdicionYBajaDeDeporte(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def setUp(self):
        self.client.force_login(self.datos["admin"])

    def test_get_editar_precarga_el_formulario(self):
        respuesta = self.client.get(reverse("editar_deporte", args=[self.datos["deporte"].id]))
        self.assertEqual(respuesta.context["form"].instance, self.datos["deporte"])

    def test_post_editar_actualiza_nombre_y_descripcion(self):
        respuesta = self.client.post(
            reverse("editar_deporte", args=[self.datos["deporte"].id]),
            {"nombre": "Fútbol Sala", "descripcion": "Nueva descripción."})
        self.assertRedirects(respuesta, reverse("listar_deportes"))
        self.datos["deporte"].refresh_from_db()
        self.assertEqual(self.datos["deporte"].nombre, "Fútbol Sala")
        self.assertEqual(self.datos["deporte"].descripcion, "Nueva descripción.")

    def test_post_editar_invalido_no_guarda_cambios(self):
        otro = Deporte.objects.create(nombre="Básquet")
        respuesta = self.client.post(
            reverse("editar_deporte", args=[otro.id]), {"nombre": self.datos["deporte"].nombre})
        self.assertEqual(respuesta.status_code, 200)
        otro.refresh_from_db()
        self.assertEqual(otro.nombre, "Básquet")

    def test_get_eliminar_pide_confirmacion_sin_borrar(self):
        respuesta = self.client.get(reverse("eliminar_deporte", args=[self.datos["deporte"].id]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(Deporte.objects.filter(pk=self.datos["deporte"].id).exists())

    def test_post_eliminar_lo_borra(self):
        desechable = Deporte.objects.create(nombre="Deporte desechable")
        respuesta = self.client.post(reverse("eliminar_deporte", args=[desechable.id]))
        self.assertRedirects(respuesta, reverse("listar_deportes"))
        self.assertFalse(Deporte.objects.filter(pk=desechable.id).exists())

    def test_un_delegado_no_puede_editar_ni_eliminar(self):
        self.client.force_login(self.datos["delegado"])
        self.assertEqual(
            self.client.get(reverse("editar_deporte", args=[self.datos["deporte"].id])).status_code, 302)
        self.assertEqual(
            self.client.post(reverse("eliminar_deporte", args=[self.datos["deporte"].id])).status_code, 302)
        self.assertTrue(Deporte.objects.filter(pk=self.datos["deporte"].id).exists())
