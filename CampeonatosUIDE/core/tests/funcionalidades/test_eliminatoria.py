"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class CuadroDeEliminatoriaAvanzaSolo(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _cuadro(self, equipos, nombre="Copa"):
        camp = _campeonato_para_calendario(
            nombre, self.datos["deporte"], ["LUNES", "MIERCOLES", "VIERNES"],
            tipo="ELIMINATORIA")
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], equipos)
        generar_fixture_eliminatoria(camp.id)
        return camp

    def _ronda(self, camp, numero):
        return list(Partido.objects.filter(campeonato=camp, ronda=numero)
                    .order_by("fecha", "hora", "id"))

    def test_la_primera_ronda_queda_marcada_como_ronda_1(self):
        camp = self._cuadro(8)
        self.assertEqual(len(self._ronda(camp, 1)), 4)

    def test_ocho_equipos_llegan_hasta_la_final(self):
        """4 cuartos + 2 semifinales + 1 final = 7 partidos."""
        camp = self._cuadro(8)

        for partido in self._ronda(camp, 1):
            _cerrar(partido, 2, 1)          # gana siempre el local
        semifinales = self._ronda(camp, 2)
        self.assertEqual(len(semifinales), 2, "deben crearse 2 semifinales solas")

        for partido in semifinales:
            _cerrar(partido, 3, 0)
        final = self._ronda(camp, 3)
        self.assertEqual(len(final), 1, "debe crearse la final sola")

        _cerrar(final[0], 1, 0)
        self.assertEqual(Partido.objects.filter(campeonato=camp).count(), 7)
        self.assertEqual(self._ronda(camp, 4), [], "despues de la final no hay mas")

    def test_no_avanza_hasta_que_termina_toda_la_ronda(self):
        camp = self._cuadro(8)
        cuartos = self._ronda(camp, 1)
        for partido in cuartos[:3]:
            _cerrar(partido, 1, 0)
        self.assertEqual(self._ronda(camp, 2), [],
                         "con un partido sin jugar no debe cruzarse nada")

        _cerrar(cuartos[3], 1, 0)
        self.assertEqual(len(self._ronda(camp, 2)), 2)

    def test_un_empate_bloquea_el_avance(self):
        """Sin penaltis ni desempate, un empate no puede decidir quien pasa."""
        camp = self._cuadro(4)
        for partido in self._ronda(camp, 1):
            _cerrar(partido, 1, 1)
        self.assertEqual(self._ronda(camp, 2), [],
                         "un empate no debe generar la ronda siguiente")

    def test_corregir_el_empate_desbloquea(self):
        camp = self._cuadro(4)
        primera = self._ronda(camp, 1)
        for partido in primera:
            _cerrar(partido, 1, 1)
        self.assertEqual(self._ronda(camp, 2), [])

        for partido in primera:
            _cerrar(partido, 2, 1)
        self.assertEqual(len(self._ronda(camp, 2)), 1, "ya hay ganadores: se crea la final")

    def test_los_equipos_con_bye_entran_en_la_segunda_ronda(self):
        """Con 5 equipos, 3 descansan en la primera ronda."""
        camp = self._cuadro(5)
        primera = self._ronda(camp, 1)
        self.assertEqual(len(primera), 1, "5 equipos -> 8 plazas -> 1 solo cruce")

        _cerrar(primera[0], 2, 0)
        segunda = self._ronda(camp, 2)
        self.assertEqual(len(segunda), 2, "el ganador y los 3 que descansaron son 4")

        jugaron = {e for p in segunda for e in (p.equipo_local_id, p.equipo_visitante_id)}
        self.assertEqual(len(jugaron), 4)
        self.assertNotIn(primera[0].equipo_visitante_id, jugaron,
                         "el eliminado no puede reaparecer")

    def test_el_perdedor_no_vuelve_a_jugar(self):
        camp = self._cuadro(8)
        perdedores = set()
        for partido in self._ronda(camp, 1):
            _cerrar(partido, 3, 1)
            perdedores.add(partido.equipo_visitante_id)

        for partido in self._ronda(camp, 2):
            self.assertNotIn(partido.equipo_local_id, perdedores)
            self.assertNotIn(partido.equipo_visitante_id, perdedores)

    def test_la_ronda_siguiente_respeta_los_dias_permitidos(self):
        camp = _campeonato_para_calendario(
            "Copa sabados", self.datos["deporte"], ["SABADO"], tipo="ELIMINATORIA")
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_eliminatoria(camp.id)
        for partido in self._ronda(camp, 1):
            _cerrar(partido, 1, 0)
        for partido in self._ronda(camp, 2):
            self.assertEqual(partido.fecha.weekday(), 5)

    def test_la_ronda_siguiente_se_juega_despues(self):
        camp = self._cuadro(4)
        primera = self._ronda(camp, 1)
        for partido in primera:
            _cerrar(partido, 1, 0)
        ultima_de_la_primera = max(p.fecha for p in primera)
        for partido in self._ronda(camp, 2):
            self.assertGreater(partido.fecha, ultima_de_la_primera)

    def test_una_liga_no_se_ve_afectada(self):
        """El avance solo aplica a ELIMINATORIA."""
        camp = _campeonato_para_calendario(
            "Liga intacta", self.datos["deporte"], ["LUNES", "MIERCOLES"])
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_liga(camp.id)
        antes = Partido.objects.filter(campeonato=camp).count()
        for partido in Partido.objects.filter(campeonato=camp):
            _cerrar(partido, 2, 1)
        self.assertEqual(Partido.objects.filter(campeonato=camp).count(), antes,
                         "una liga no debe generar rondas nuevas")


class BotonManualDeAvance(PruebaBase):
    """Respaldo por si el avance automatico no se hubiera disparado."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _cuadro_con_ronda_cerrada(self):
        camp = _campeonato_para_calendario(
            "Copa boton", self.datos["deporte"], ["LUNES", "MIERCOLES"],
            tipo="ELIMINATORIA")
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_eliminatoria(camp.id)
        return camp

    def test_el_boton_crea_la_ronda_si_falta(self):
        camp = self._cuadro_con_ronda_cerrada()
        # Se cierran los partidos sin pasar por el save() del modelo, de modo
        # que la senal no salta: simula el caso que el boton debe cubrir.
        for partido in Partido.objects.filter(campeonato=camp, ronda=1):
            Partido.objects.filter(pk=partido.pk).update(
                resultado_local=2, resultado_visitante=0, estado="FINALIZADO")
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 0)

        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(
            reverse("avanzar_ronda_eliminatoria", args=[camp.id]))
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 1)

    def test_pulsarlo_dos_veces_no_duplica(self):
        camp = self._cuadro_con_ronda_cerrada()
        for partido in Partido.objects.filter(campeonato=camp, ronda=1):
            _cerrar(partido, 2, 0)
        self.client.force_login(self.datos["admin"])
        url = reverse("avanzar_ronda_eliminatoria", args=[camp.id])
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 1,
                         "no debe crear la misma ronda dos veces")

    def test_un_jugador_no_puede_usarlo(self):
        camp = self._cuadro_con_ronda_cerrada()
        self.client.force_login(self.datos["jugador"].usuario)
        respuesta = self.client.post(
            reverse("avanzar_ronda_eliminatoria", args=[camp.id]))
        self.assertIn(respuesta.status_code, (302, 403))
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 0)

    def test_avisa_cuando_hay_un_empate(self):
        camp = self._cuadro_con_ronda_cerrada()
        for partido in Partido.objects.filter(campeonato=camp, ronda=1):
            Partido.objects.filter(pk=partido.pk).update(
                resultado_local=1, resultado_visitante=1, estado="FINALIZADO")
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(
            reverse("avanzar_ronda_eliminatoria", args=[camp.id]), follow=True)
        textos = [m.message for m in respuesta.context["messages"]]
        self.assertTrue(any("empatado" in t for t in textos),
                        f"deberia explicar el empate: {textos}")

    def test_avisa_cuando_la_ronda_sigue_en_juego(self):
        camp = self._cuadro_con_ronda_cerrada()
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(
            reverse("avanzar_ronda_eliminatoria", args=[camp.id]), follow=True)
        textos = [m.message for m in respuesta.context["messages"]]
        self.assertTrue(any("sin jugar" in t for t in textos),
                        f"deberia decir que faltan partidos: {textos}")

    def test_el_boton_aparece_solo_en_eliminatoria(self):
        camp = self._cuadro_con_ronda_cerrada()
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(
            reverse("fixture_campeonato_detalle", args=[camp.id]))
        self.assertTrue(respuesta.context["puede_avanzar_ronda"])

        liga = _campeonato_para_calendario(
            "Liga sin boton", self.datos["deporte"], ["LUNES"])
        _equipos_para_calendario(
            liga, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_liga(liga.id)
        respuesta = self.client.get(
            reverse("fixture_campeonato_detalle", args=[liga.id]))
        self.assertFalse(respuesta.context["puede_avanzar_ronda"])


# ---------------------------------------------------------------------------
# Tanda de penaltis.
#
# Un empate no puede decidir quien pasa de ronda. La tanda es lo unico que
# lo resuelve, y no cuenta como goles: no debe tocar la tabla de posiciones.
# ---------------------------------------------------------------------------

