"""Bug real: comparar el nombre del deporte con tildes rompia las stats.

equipo_views.py, jugador_views.py y Equipo.puntos_totales comparaban
`campeonato.deporte.nombre.upper()` contra literales SIN tilde
("FUTBOL"). El deporte de _datos_base() (y el que crea el propio
formulario de alta de deportes, en su ortografia natural) se llama
"Fútbol", con tilde: la comparacion nunca coincidia y las estadisticas
de futbol (goles por jugador, puntos por partido) quedaban siempre en
cero o None, sin ningun error visible.
"""
from core.tests.base import *  # noqa: F401,F403


class ElNombreDelDeporteConTildeSigueFuncionando(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_el_deporte_de_base_se_llama_futbol_con_tilde(self):
        """Ancla del bug: si esto deja de ser cierto, el test ya no prueba nada."""
        self.assertEqual(self.datos["deporte"].nombre, "Fútbol")

    def test_puntos_totales_cuenta_la_victoria_con_tilde_en_el_deporte(self):
        rival = Equipo.objects.filter(
            campeonato=self.datos["campeonato"]).exclude(pk=self.datos["equipo"].pk).first()
        Partido.objects.create(
            campeonato=self.datos["campeonato"], equipo_local=self.datos["equipo"],
            equipo_visitante=rival, fecha=date.today(), hora=time(18, 0),
            lugar="Cancha 1", resultado_local=2, resultado_visitante=0,
            estado="FINALIZADO")
        self.assertEqual(self.datos["equipo"].puntos_totales, 3)

    def test_ver_equipo_jugador_muestra_las_estadisticas_de_futbol(self):
        EstadisticaJugadorFutbol.objects.create(
            campeonato=self.datos["campeonato"], jugador=self.datos["jugador"], goles=7)
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(
            reverse("ver_equipo_jugador", args=[self.datos["equipo"].id]))
        fila = next(d for d in respuesta.context["jugadores_data"]
                    if d["jugador"] == self.datos["jugador"])
        self.assertIsNotNone(fila["stats"], "las stats no deben perderse por la tilde")
        self.assertEqual(fila["stats"].goles, 7)

    def test_ver_estadisticas_jugador_muestra_las_de_futbol(self):
        EstadisticaJugadorFutbol.objects.create(
            campeonato=self.datos["campeonato"], jugador=self.datos["jugador"], goles=4)
        self.client.force_login(self.datos["jugador"].usuario)
        respuesta = self.client.get(
            reverse("ver_estadisticas_jugador", args=[self.datos["jugador"].id]))
        self.assertIsNotNone(respuesta.context["estadisticas"])
        self.assertEqual(respuesta.context["estadisticas"].goles, 4)
