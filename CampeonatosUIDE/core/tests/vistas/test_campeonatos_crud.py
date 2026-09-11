"""Huecos reales de campeonato_views.py (72% de cobertura medida): CRUD de
Campeonato, el caso 'no es de eliminatoria' de AvanzarRondaEliminatoria,
el rechazo de GenerarFixtureCampeonato con menos de 2 equipos, y las
exportaciones de tabla de posiciones con partidos ya finalizados (con
_datos_base() solo hay partidos PROGRAMADO, asi que esas ramas nunca se
ejecutaban en el resto de la suite).
"""
from core.tests.base import *  # noqa: F401,F403


def _datos_campeonato(deporte, **extra):
    hoy = date.today()
    return {
        "nombre": "Campeonato de prueba CRUD", "tipo_campeonato": "LIGA",
        "descripcion": "Descripción de prueba.",
        "fecha_inicio": hoy, "fecha_fin": hoy + timedelta(days=60),
        "estado": "INSCRIPCION", "deporte": deporte.pk,
        "max_jugadores_por_equipo": 11, "precio_inscripcion": "0",
        "activo": "SI", "es_publico": "SI",
        **extra,
    }


class AltaEdicionYBajaDeCampeonato(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def setUp(self):
        self.client.force_login(self.datos["admin"])

    def test_un_anonimo_no_puede_crear_campeonatos(self):
        self.client.logout()
        antes = Campeonato.objects.count()
        self.client.post(reverse("crear_campeonato"), _datos_campeonato(self.datos["deporte"]))
        self.assertEqual(Campeonato.objects.count(), antes)

    def test_post_valido_crea_el_campeonato(self):
        respuesta = self.client.post(
            reverse("crear_campeonato"), _datos_campeonato(self.datos["deporte"]))
        self.assertRedirects(respuesta, reverse("listar_campeonatos"))
        self.assertTrue(Campeonato.objects.filter(nombre="Campeonato de prueba CRUD").exists())

    def test_post_invalido_no_crea_nada(self):
        antes = Campeonato.objects.count()
        respuesta = self.client.post(reverse("crear_campeonato"), {})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Campeonato.objects.count(), antes)

    def test_fecha_fin_antes_de_inicio_no_pasa(self):
        hoy = date.today()
        antes = Campeonato.objects.count()
        respuesta = self.client.post(reverse("crear_campeonato"), _datos_campeonato(
            self.datos["deporte"], fecha_inicio=hoy, fecha_fin=hoy - timedelta(days=1)))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Campeonato.objects.count(), antes)

    def test_editar_actualiza_el_nombre(self):
        respuesta = self.client.post(
            reverse("editar_campeonato", args=[self.datos["campeonato"].id]),
            _datos_campeonato(self.datos["deporte"], nombre="Nombre editado"))
        self.assertRedirects(respuesta, reverse("listar_campeonatos"))
        self.datos["campeonato"].refresh_from_db()
        self.assertEqual(self.datos["campeonato"].nombre, "Nombre editado")

    def test_get_eliminar_pide_confirmacion_sin_borrar(self):
        respuesta = self.client.get(reverse("eliminar_campeonato", args=[self.datos["campeonato"].id]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(Campeonato.objects.filter(pk=self.datos["campeonato"].id).exists())

    def test_post_eliminar_lo_borra(self):
        desechable = _campeonato_para_calendario("Desechable", self.datos["deporte"], ["LUNES"])
        respuesta = self.client.post(reverse("eliminar_campeonato", args=[desechable.id]))
        self.assertRedirects(respuesta, reverse("listar_campeonatos"))
        self.assertFalse(Campeonato.objects.filter(pk=desechable.id).exists())


class GenerarFixtureRequiereDosEquiposAprobados(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_con_menos_de_dos_equipos_no_genera_nada(self):
        campeonato = _campeonato_para_calendario("Un solo equipo", self.datos["deporte"], ["LUNES"])
        _equipos_para_calendario(campeonato, self.datos["carrera"], self.datos["delegado"], 1)
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(reverse("generar_fixture_campeonato", args=[campeonato.id]))
        self.assertRedirects(
            respuesta, reverse("fixture_campeonato_detalle", args=[campeonato.id]))
        self.assertEqual(Partido.objects.filter(campeonato=campeonato).count(), 0)


class AvanzarRondaEnUnaLigaNoHaceNada(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_avisa_que_no_es_de_eliminatoria(self):
        liga = _campeonato_para_calendario("Liga no eliminatoria", self.datos["deporte"], ["LUNES"])
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(
            reverse("avanzar_ronda_eliminatoria", args=[liga.id]), follow=True)
        textos = [m.message for m in respuesta.context["messages"]]
        self.assertTrue(any("no es de eliminatoria" in t for t in textos), textos)


class ExportacionesDeTablaDePosiciones(PruebaBase):
    """Con partidos FINALIZADO reales, para ejercitar el calculo de PJ/PG/etc
    que _datos_base() (partido PROGRAMADO) nunca ejecutaba."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.rival = Equipo.objects.filter(
            campeonato=cls.datos["campeonato"]).exclude(pk=cls.datos["equipo"].pk).first()
        Partido.objects.create(
            campeonato=cls.datos["campeonato"], equipo_local=cls.datos["equipo"],
            equipo_visitante=cls.rival, fecha=date.today(), hora=time(18, 0),
            lugar="Cancha 1", resultado_local=2, resultado_visitante=1,
            estado="FINALIZADO")

    def setUp(self):
        self.client.force_login(self.datos["admin"])

    def test_exportar_pdf_responde_con_ese_content_type(self):
        respuesta = self.client.get(
            reverse("export_tabla_posiciones_pdf", args=[self.datos["campeonato"].id]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta["Content-Type"], "application/pdf")

    def test_exportar_excel_responde_con_ese_content_type(self):
        respuesta = self.client.get(
            reverse("export_tabla_posiciones_excel", args=[self.datos["campeonato"].id]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("spreadsheetml", respuesta["Content-Type"])

    def test_un_delegado_ajeno_no_puede_exportar(self):
        ajeno = Usuario.objects.create_user(
            username="delegado_export", email="dex@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="masculino")
        self.client.force_login(ajeno)
        respuesta = self.client.get(
            reverse("export_tabla_posiciones_pdf", args=[self.datos["campeonato"].id]))
        self.assertEqual(respuesta.status_code, 302)
