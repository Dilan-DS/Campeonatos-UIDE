"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class ReglasDeLaTandaDePenales(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _partido(self, gl, gv, pl=None, pv=None):
        camp = self.datos["campeonato"]
        return Partido(
            campeonato=camp,
            equipo_local=self.datos["equipo"],
            equipo_visitante=Equipo.objects.filter(campeonato=camp)
                                           .exclude(pk=self.datos["equipo"].pk).first(),
            fecha=date.today(), hora=time(18, 0), lugar="Cancha 1",
            resultado_local=gl, resultado_visitante=gv,
            penales_local=pl, penales_visitante=pv)

    def test_sin_tanda_es_valido(self):
        self._partido(2, 1).clean()
        self._partido(1, 1).clean()

    def test_la_tanda_exige_los_dos_equipos(self):
        with self.assertRaises(ValidationError) as caso:
            self._partido(1, 1, pl=4).clean()
        self.assertIn("los dos equipos", caso.exception.messages[0])

        with self.assertRaises(ValidationError):
            self._partido(1, 1, pv=4).clean()

    def test_la_tanda_solo_vale_si_hay_empate(self):
        with self.assertRaises(ValidationError) as caso:
            self._partido(2, 1, pl=5, pv=4).clean()
        self.assertIn("empatado", caso.exception.messages[0])

    def test_la_tanda_no_puede_quedar_igualada(self):
        with self.assertRaises(ValidationError) as caso:
            self._partido(1, 1, pl=3, pv=3).clean()
        self.assertIn("ganador", caso.exception.messages[0])

    def test_una_tanda_correcta_pasa(self):
        self._partido(1, 1, pl=5, pv=4).clean()

    def test_ganador_por_penales(self):
        self.assertEqual(self._partido(1, 1, pl=5, pv=4).ganador_por_penales(),
                         self.datos["equipo"])
        self.assertIsNone(self._partido(1, 1).ganador_por_penales())


class LaTandaDecideQuienPasaDeRonda(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _cuadro(self, nombre="Copa penales"):
        camp = _campeonato_para_calendario(
            nombre, self.datos["deporte"], ["LUNES", "MIERCOLES", "VIERNES"],
            tipo="ELIMINATORIA")
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_eliminatoria(camp.id)
        return camp

    def test_un_empate_con_tanda_avanza_solo(self):
        camp = self._cuadro()
        primera = list(Partido.objects.filter(campeonato=camp, ronda=1)
                       .order_by("fecha", "hora", "id"))
        ganadores = []
        for partido in primera:
            partido.resultado_local = 1
            partido.resultado_visitante = 1
            partido.penales_local = 5
            partido.penales_visitante = 3
            partido.estado = "FINALIZADO"
            partido.save()
            ganadores.append(partido.equipo_local_id)

        final = list(Partido.objects.filter(campeonato=camp, ronda=2))
        self.assertEqual(len(final), 1, "la tanda debe desbloquear la ronda")
        self.assertCountEqual(
            [final[0].equipo_local_id, final[0].equipo_visitante_id], ganadores,
            "deben pasar los ganadores de la tanda, no los locales por defecto")

    def test_pasa_el_visitante_si_gana_la_tanda(self):
        camp = self._cuadro("Copa visitante")
        primera = list(Partido.objects.filter(campeonato=camp, ronda=1))
        esperados = []
        for partido in primera:
            partido.resultado_local = 2
            partido.resultado_visitante = 2
            partido.penales_local = 2
            partido.penales_visitante = 4
            partido.estado = "FINALIZADO"
            partido.save()
            esperados.append(partido.equipo_visitante_id)

        final = Partido.objects.filter(campeonato=camp, ronda=2).first()
        self.assertCountEqual(
            [final.equipo_local_id, final.equipo_visitante_id], esperados)

    def test_sin_tanda_sigue_bloqueado(self):
        camp = self._cuadro("Copa bloqueada")
        for partido in Partido.objects.filter(campeonato=camp, ronda=1):
            partido.resultado_local = 1
            partido.resultado_visitante = 1
            partido.estado = "FINALIZADO"
            partido.save()
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 0)

    def test_anotar_la_tanda_despues_desbloquea(self):
        """El arbitro cierra el acta empatada y luego anota la tanda."""
        camp = self._cuadro("Copa tardia")
        primera = list(Partido.objects.filter(campeonato=camp, ronda=1))
        for partido in primera:
            partido.resultado_local = 0
            partido.resultado_visitante = 0
            partido.estado = "FINALIZADO"
            partido.save()
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 0)

        for partido in primera:
            partido.penales_local = 4
            partido.penales_visitante = 2
            partido.save()
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 1)


class ElArbitroAnotaLaTandaDesdeElActa(PruebaBase):
    """El acta es la unica via enrutada para cerrar un partido.

    La URL registrar_resultado_partido apunta en realidad a
    acta_partido_arbitro; la funcion registrar_resultado_partido de
    arbitro_views no la enruta nadie.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _partido_de_eliminatoria(self, nombre):
        camp = _campeonato_para_calendario(
            nombre, self.datos["deporte"], ["LUNES", "MIERCOLES"],
            tipo="ELIMINATORIA")
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_eliminatoria(camp.id)
        partido = Partido.objects.filter(campeonato=camp, ronda=1).first()
        partido.arbitro = self.datos["arbitro"]
        partido.save()
        return partido

    def _enviar(self, partido, datos):
        # Los equipos de estos campeonatos no tienen jugadores, asi que la
        # suma de goles por jugador es 0 y el acta solo cuadra con un 0-0.
        self.client.force_login(self.datos["arbitro"].usuario)
        return self.client.post(
            reverse("registrar_resultado_partido", args=[partido.id]), datos)

    def test_guarda_la_tanda(self):
        partido = self._partido_de_eliminatoria("Acta tanda")
        self._enviar(partido, {"resultado_local": "0", "resultado_visitante": "0",
                               "penales_local": "5", "penales_visitante": "4"})
        partido.refresh_from_db()
        self.assertEqual((partido.penales_local, partido.penales_visitante), (5, 4))
        self.assertEqual(partido.estado, "FINALIZADO")

    def test_rechaza_una_tanda_igualada(self):
        partido = self._partido_de_eliminatoria("Acta igualada")
        self._enviar(partido, {"resultado_local": "0", "resultado_visitante": "0",
                               "penales_local": "3", "penales_visitante": "3"})
        partido.refresh_from_db()
        self.assertIsNone(partido.penales_local,
                          "una tanda igualada no debe guardarse")
        self.assertNotEqual(partido.estado, "FINALIZADO")

    def test_rechaza_penaltis_sin_empate(self):
        partido = self._partido_de_eliminatoria("Acta sin empate")
        self._enviar(partido, {"resultado_local": "1", "resultado_visitante": "0",
                               "penales_local": "5", "penales_visitante": "4"})
        partido.refresh_from_db()
        self.assertIsNone(partido.penales_local)

    def test_un_partido_normal_se_guarda_sin_tanda(self):
        """El flujo de siempre no debe cambiar."""
        partido = self._partido_de_eliminatoria("Acta normal")
        self._enviar(partido, {"resultado_local": "0", "resultado_visitante": "0"})
        partido.refresh_from_db()
        self.assertEqual(partido.estado, "FINALIZADO")
        self.assertIsNone(partido.penales_local)

    def test_el_acta_valida_la_tanda(self):
        from core.forms import ArbitroActaForm

        formulario = ArbitroActaForm(data={
            "resultado_local": "1", "resultado_visitante": "1",
            "penales_local": "3", "penales_visitante": "3"})
        self.assertFalse(formulario.is_valid())
        self.assertIn("penales_local", formulario.errors)

        correcto = ArbitroActaForm(data={
            "resultado_local": "1", "resultado_visitante": "1",
            "penales_local": "5", "penales_visitante": "3"})
        self.assertTrue(correcto.is_valid(), correcto.errors.as_text())



# ---------------------------------------------------------------------------
# Imports de las vistas.
#
# core/urls.py hacia `from .views import *` y core/views/__init__.py
# encadenaba otros dieciocho comodines. Cuando dos modulos definian una
# funcion con el mismo nombre, el ultimo importado se quedaba con el nombre
# y el otro dejaba de existir sin ningun aviso: asi quedaron inalcanzables
# detalle_equipo (jugador_views) y registrar_resultado_partido
# (arbitro_views), con aspecto de codigo en uso.
# ---------------------------------------------------------------------------

