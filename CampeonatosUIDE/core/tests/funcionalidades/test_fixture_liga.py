"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class NoHayDosPartidosEnLaMismaCanchaYHora(PruebaBase):
    """Toda la jornada se creaba a las 18:00 con Cancha aleatoria 1-5.

    Dos partidos de la misma jornada podian caer a la vez en la misma
    cancha.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_sin_solapes_de_cancha(self):
        for n in (4, 6, 8, 10, 12):
            with self.subTest(equipos=n):
                camp = _campeonato_para_calendario(
                    f"Canchas {n}", self.datos["deporte"], ["LUNES"])
                _equipos_para_calendario(
                    camp, self.datos["carrera"], self.datos["delegado"], n)
                generar_fixture_liga(camp.id)

                ocupacion = [
                    (p.fecha, p.hora, p.lugar)
                    for p in Partido.objects.filter(campeonato=camp)
                ]
                self.assertEqual(len(ocupacion), len(set(ocupacion)),
                                 "dos partidos no pueden compartir fecha, hora y cancha")

    def test_los_primeros_cinco_van_a_las_seis(self):
        """Con cinco canchas libres no hace falta mover la hora."""
        camp = _campeonato_para_calendario(
            "Canchas horario", self.datos["deporte"], ["LUNES"])
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 10)
        generar_fixture_liga(camp.id)
        primera_jornada = Partido.objects.filter(campeonato=camp).order_by("fecha")[:5]
        self.assertTrue(all(p.hora.hour == 18 for p in primera_jornada))
        self.assertEqual(
            sorted(p.lugar for p in primera_jornada),
            ["Cancha 1", "Cancha 2", "Cancha 3", "Cancha 4", "Cancha 5"])


class ElEmparejamientoSigueSiendoCorrecto(PruebaBase):
    """Red de seguridad del algoritmo: los arreglos no deben alterarlo."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_todos_contra_todos(self):
        for n in (2, 3, 4, 5, 6, 8):
            with self.subTest(equipos=n):
                camp = _campeonato_para_calendario(
                    f"Liga check {n}", self.datos["deporte"], ["LUNES", "MIERCOLES", "VIERNES"])
                _equipos_para_calendario(
                    camp, self.datos["carrera"], self.datos["delegado"], n)
                creados = generar_fixture_liga(camp.id)
                self.assertEqual(creados, n * (n - 1) // 2)

                partidos = list(Partido.objects.filter(campeonato=camp))
                parejas = [frozenset((p.equipo_local_id, p.equipo_visitante_id))
                           for p in partidos]
                self.assertEqual(len(parejas), len(set(parejas)))
                for p in partidos:
                    self.assertNotEqual(p.equipo_local_id, p.equipo_visitante_id)

    def test_nadie_juega_dos_veces_el_mismo_dia(self):
        camp = _campeonato_para_calendario(
            "Liga dias check", self.datos["deporte"], ["LUNES", "MIERCOLES"])
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 6)
        generar_fixture_liga(camp.id)
        por_dia = {}
        for p in Partido.objects.filter(campeonato=camp):
            por_dia.setdefault(p.fecha, []).extend(
                [p.equipo_local_id, p.equipo_visitante_id])
        for fecha, equipos in por_dia.items():
            self.assertEqual(len(equipos), len(set(equipos)), f"solape el {fecha}")

    def test_solo_dias_permitidos(self):
        camp = _campeonato_para_calendario(
            "Liga sabados", self.datos["deporte"], ["SABADO"])
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_liga(camp.id)
        for p in Partido.objects.filter(campeonato=camp):
            self.assertEqual(p.fecha.weekday(), 5)

    def test_los_generos_no_se_cruzan(self):
        camp = _campeonato_para_calendario(
            "Liga mixta check", self.datos["deporte"], ["LUNES", "MIERCOLES"])
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4, "masculino")
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4, "femenino")
        self.assertEqual(generar_fixture_liga(camp.id), 12)
        for p in Partido.objects.filter(campeonato=camp):
            self.assertEqual(p.equipo_local.genero, p.equipo_visitante.genero)


# ---------------------------------------------------------------------------
# Avance del cuadro de eliminatoria.
#
# generar_fixture_eliminatoria solo creaba la primera ronda: con 8 equipos
# programaba 4 cruces y ahi se quedaba, cuando el cuadro completo necesita
# 7 partidos. Ahora los ganadores cruzan solos al cerrarse la ronda, y hay
# un boton manual de respaldo.
# ---------------------------------------------------------------------------

