"""Vistas que existian pero estaban inutilizables por distintos motivos.

registrar_partido hacia `raise PermissionDenied` incondicional: el boton
"Registrar Partido" de listar_partidos.html llevaba a un 403 seguro, sin
plantilla ni formulario detras.

RegistrarPagoParaEquipoAdminView existia y funcionaba, pero no tenia
ninguna URL asignada en core/urls.py: un admin no podia llegar a ella
desde ningun lado.
"""
from core.tests.base import *  # noqa: F401,F403


class RegistrarPartidoYaFunciona(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _datos_partido(self, **extra):
        return {
            "campeonato": self.datos["campeonato"].pk,
            "equipo_local": self.datos["equipo"].pk,
            "equipo_visitante": Equipo.objects.filter(
                campeonato=self.datos["campeonato"]).exclude(pk=self.datos["equipo"].pk).first().pk,
            "fecha": date.today() + timedelta(days=20),
            "hora": "18:00",
            "lugar": "Cancha nueva",
            "estado": "PROGRAMADO",
            **extra,
        }

    def test_el_listado_ya_no_lleva_a_un_403(self):
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(reverse("registrar_partido"))
        self.assertEqual(respuesta.status_code, 200)

    def test_un_admin_registra_un_partido(self):
        self.client.force_login(self.datos["admin"])
        antes = Partido.objects.count()
        respuesta = self.client.post(reverse("registrar_partido"), self._datos_partido())
        self.assertRedirects(respuesta, reverse("listar_partidos"))
        self.assertEqual(Partido.objects.count(), antes + 1)

    def test_un_delegado_no_puede_registrar_un_partido(self):
        """user_passes_test redirige a login en vez de devolver 403."""
        self.client.force_login(self.datos["delegado"])
        antes = Partido.objects.count()
        respuesta = self.client.post(reverse("registrar_partido"), self._datos_partido())
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(Partido.objects.count(), antes)

    def test_datos_invalidos_no_crean_nada(self):
        self.client.force_login(self.datos["admin"])
        antes = Partido.objects.count()
        self.client.post(reverse("registrar_partido"), self._datos_partido(fecha=""))
        self.assertEqual(Partido.objects.count(), antes)


class RegistrarPagoParaEquipoAdminYaTieneRuta(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.equipo_sin_pago = Equipo.objects.create(
            nombre="Equipo admin sin pago", campeonato=cls.datos["campeonato"],
            carrera=cls.datos["carrera"], delegado=cls.datos["delegado"], aprobado=True)

    def test_el_listado_de_equipos_enlaza_a_la_nueva_ruta(self):
        self.client.force_login(self.datos["admin"])
        cuerpo = self.client.get(reverse("listar_equipos")).content.decode()
        self.assertIn(
            reverse("registrar_pago_admin_equipo", args=[self.equipo_sin_pago.id]), cuerpo)

    def test_get_muestra_el_formulario_con_el_equipo_preseleccionado(self):
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(
            reverse("registrar_pago_admin_equipo", args=[self.equipo_sin_pago.id]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["equipo"], self.equipo_sin_pago)

    def test_post_crea_el_pago_para_ese_equipo(self):
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(
            reverse("registrar_pago_admin_equipo", args=[self.equipo_sin_pago.id]),
            {"equipo": self.equipo_sin_pago.pk, "metodo": "EFECTIVO", "estado": "PENDIENTE"})
        self.assertRedirects(
            respuesta, reverse("detalle_equipo", args=[self.equipo_sin_pago.id]))
        self.assertTrue(Pago.objects.filter(equipo=self.equipo_sin_pago).exists())

    def test_un_delegado_no_puede_usar_la_ruta_de_admin(self):
        self.client.force_login(self.datos["delegado"])
        respuesta = self.client.get(
            reverse("registrar_pago_admin_equipo", args=[self.equipo_sin_pago.id]))
        self.assertEqual(respuesta.status_code, 302)
        self.assertFalse(Pago.objects.filter(equipo=self.equipo_sin_pago).exists())
