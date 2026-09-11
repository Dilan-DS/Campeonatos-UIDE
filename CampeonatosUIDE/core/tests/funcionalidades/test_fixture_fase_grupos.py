"""Cobertura de generar_fixture_fase_grupos.

Este generador no tenia ninguna prueba (0% de cobertura real medida con
`coverage`), a diferencia de liga y eliminatoria. Solo se prueba el
comportamiento que el codigo realmente implementa: agrupa por genero en
hasta 4 grupos, arma UNA sola ronda de emparejamientos por grupo (no todos
contra todos) y usa BYE si un grupo queda impar.
"""

from core.tests.base import *  # noqa: F401,F403
from core.utils.generar_fixture_fase_grupos import generar_fixture_fase_grupos


class GeneradorDeFaseDeGruposFaltante(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _campeonato(self, nombre, dias=("LUNES", "MIERCOLES")):
        return _campeonato_para_calendario(
            nombre, self.datos["deporte"], list(dias), tipo="FASE_GRUPOS")

    def test_campeonato_inexistente_devuelve_cero(self):
        self.assertEqual(generar_fixture_fase_grupos(999999), 0)

    def test_un_solo_equipo_no_genera_partidos(self):
        camp = self._campeonato("Grupos un equipo")
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 1)
        self.assertEqual(generar_fixture_fase_grupos(camp.id), 0)

    def test_siempre_devuelve_entero(self):
        camp = self._campeonato("Grupos vacio")
        resultado = generar_fixture_fase_grupos(camp.id)
        self.assertIsInstance(resultado, int)
        self.assertEqual(resultado, 0)

    def test_cuatro_equipos_forman_dos_grupos_de_dos(self):
        """4 equipos -> num_grupos = min(4, 4//2) = 2 grupos de 2 -> 2 partidos."""
        camp = self._campeonato("Grupos cuatro")
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4)
        creados = generar_fixture_fase_grupos(camp.id)
        self.assertEqual(creados, 2)
        self.assertEqual(Partido.objects.filter(campeonato=camp).count(), 2)

    def test_tres_equipos_con_bye_genera_un_solo_partido(self):
        """Grupo impar de 3 -> se agrega un BYE (None); el par sin BYE juega."""
        camp = self._campeonato("Grupos tres")
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 3)
        creados = generar_fixture_fase_grupos(camp.id)
        self.assertEqual(creados, 1)

    def test_generos_no_se_cruzan(self):
        camp = self._campeonato("Grupos mixtos")
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 2, genero="masculino")
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 2, genero="femenino")
        generar_fixture_fase_grupos(camp.id)
        for partido in Partido.objects.filter(campeonato=camp):
            self.assertEqual(partido.equipo_local.genero, partido.equipo_visitante.genero)

    def test_respeta_los_dias_permitidos(self):
        camp = self._campeonato("Grupos sabado", dias=("SABADO",))
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_fase_grupos(camp.id)
        for partido in Partido.objects.filter(campeonato=camp):
            self.assertEqual(partido.fecha.weekday(), 5, "SABADO es el indice 5")

    def test_solo_incluye_equipos_aprobados(self):
        camp = self._campeonato("Grupos no aprobados")
        equipos = _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4)
        equipos[0].aprobado = False
        equipos[0].save()
        generar_fixture_fase_grupos(camp.id)
        for partido in Partido.objects.filter(campeonato=camp):
            self.assertNotIn(equipos[0].id, (partido.equipo_local_id, partido.equipo_visitante_id))
