"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class TablaDePosicionesCalculaBien(PruebaBase):
    """Puntos, diferencia de goles y desempate de calcular_tabla_posiciones.

    Es el calculo que decide quien gana el campeonato, asi que se comprueba
    con un escenario de resultado conocido en lugar de solo mirar que la
    pagina responda.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.camp = _campeonato_vacio("Liga de calculo", cls.datos["deporte"])

        def equipo(nombre, aprobado=True):
            return Equipo.objects.create(
                nombre=nombre, campeonato=cls.camp, carrera=cls.datos["carrera"],
                delegado=cls.datos["delegado"], aprobado=aprobado)

        cls.a, cls.b, cls.c = equipo("Alfa"), equipo("Beta"), equipo("Gamma")
        cls.sin_aprobar = equipo("Delta", aprobado=False)

        hoy = date.today()

        def partido(local, visitante, gl, gv, estado, dia, hora_):
            return Partido.objects.create(
                campeonato=cls.camp, equipo_local=local, equipo_visitante=visitante,
                fecha=hoy - timedelta(days=dia), hora=time(hora_, 0),
                lugar="Cancha 1", estado=estado,
                resultado_local=gl, resultado_visitante=gv)

        partido(cls.a, cls.b, 3, 1, "FINALIZADO", 5, 10)        # gana Alfa
        partido(cls.b, cls.c, 2, 2, "FINALIZADO", 4, 11)        # empate
        partido(cls.a, cls.c, 9, 0, "PROGRAMADO", 3, 12)        # no cuenta
        partido(cls.a, cls.c, None, None, "FINALIZADO", 2, 13)  # sin marcador

    def _fila(self, tabla, equipo):
        return next(f for f in tabla if f["equipo"].pk == equipo.pk)

    def test_puntos_y_goles_por_equipo(self):
        tabla = calcular_tabla_posiciones(self.camp)

        alfa = self._fila(tabla, self.a)
        self.assertEqual(
            (alfa["pj"], alfa["pg"], alfa["pe"], alfa["pp"], alfa["puntos"]),
            (1, 1, 0, 0, 3), "una victoria son 3 puntos")
        self.assertEqual((alfa["gf"], alfa["gc"], alfa["gd"]), (3, 1, 2))

        beta = self._fila(tabla, self.b)
        self.assertEqual(
            (beta["pj"], beta["pg"], beta["pe"], beta["pp"], beta["puntos"]),
            (2, 0, 1, 1, 1), "un empate es 1 punto y la derrota ninguno")
        self.assertEqual((beta["gf"], beta["gc"], beta["gd"]), (3, 5, -2))

        gamma = self._fila(tabla, self.c)
        self.assertEqual((gamma["pj"], gamma["puntos"], gamma["gd"]), (1, 1, 0))

    def test_desempata_por_diferencia_de_goles(self):
        """Beta y Gamma tienen 1 punto; Gamma va delante por diferencia."""
        orden = [f["equipo"].nombre for f in calcular_tabla_posiciones(self.camp)]
        self.assertEqual(orden[0], "Alfa", "el lider es quien mas puntos tiene")
        self.assertLess(orden.index("Gamma"), orden.index("Beta"),
                        "con los mismos puntos manda la diferencia de goles")

    def test_ignora_partidos_no_finalizados_y_sin_resultado(self):
        """El 9-0 PROGRAMADO y el FINALIZADO sin marcador no deben sumar."""
        alfa = self._fila(calcular_tabla_posiciones(self.camp), self.a)
        self.assertEqual(alfa["pj"], 1, "solo cuenta el partido finalizado con marcador")
        self.assertEqual(alfa["gf"], 3, "el 9-0 programado no debe sumar goles")

    def test_solo_aparecen_equipos_aprobados(self):
        nombres = [f["equipo"].nombre for f in calcular_tabla_posiciones(self.camp)]
        self.assertNotIn("Delta", nombres, "un equipo sin aprobar no va en la tabla")
        self.assertEqual(len(nombres), 3)

    def test_no_mezcla_campeonatos(self):
        """Los equipos del campeonato de _datos_base no deben colarse."""
        nombres = [f["equipo"].nombre for f in calcular_tabla_posiciones(self.camp)]
        self.assertNotIn("Equipo A", nombres)


class LaTandaNoAfectaALaTablaDePosiciones(PruebaBase):
    """Los penaltis no son goles: no deben sumar en la clasificacion."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_un_empate_con_tanda_sigue_siendo_empate_en_la_tabla(self):
        camp = _campeonato_para_calendario(
            "Liga con tanda", self.datos["deporte"], ["LUNES"])
        equipos = _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 2)

        Partido.objects.create(
            campeonato=camp, equipo_local=equipos[0], equipo_visitante=equipos[1],
            fecha=date.today(), hora=time(18, 0), lugar="Cancha 1",
            resultado_local=1, resultado_visitante=1,
            penales_local=5, penales_visitante=3, estado="FINALIZADO")

        tabla = calcular_tabla_posiciones(camp)
        for fila in tabla:
            self.assertEqual(fila["puntos"], 1, "un empate da 1 punto a cada uno")
            self.assertEqual(fila["gf"], 1, "los penaltis no cuentan como goles")
            self.assertEqual(fila["pe"], 1)
            self.assertEqual(fila["pg"], 0, "la tanda no convierte el empate en victoria")

