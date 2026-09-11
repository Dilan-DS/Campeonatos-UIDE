"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class CampeonatoSinDiasNoRompe(PruebaBase):
    """dias_partido admite vacio (blank=True, default=[]).

    Con la lista vacia el bucle que buscaba fecha no terminaba: avanzaba
    hasta pasar del ano 9999 y lanzaba OverflowError, que desde la web
    salia como un error 500.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_liga_sin_dias_genera_igualmente(self):
        camp = _campeonato_para_calendario("Liga sin dias", self.datos["deporte"], [])
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4)
        creados = generar_fixture_liga(camp.id)
        self.assertEqual(creados, 6, "4 equipos son 6 partidos, con o sin dias marcados")

    def test_eliminatoria_sin_dias_genera_igualmente(self):
        camp = _campeonato_para_calendario(
            "Elim sin dias", self.datos["deporte"], [], tipo="ELIMINATORIA")
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4)
        self.assertEqual(generar_fixture_eliminatoria(camp.id), 2)

    def test_un_dia_desconocido_no_rompe(self):
        """Si el dato guardado no esta en el mapa, se permiten los siete."""
        self.assertEqual(dias_permitidos_de(_ConDias(["MIÉRCOLES"])), list(range(7)))
        self.assertEqual(dias_permitidos_de(_ConDias([])), list(range(7)))
        self.assertEqual(dias_permitidos_de(_ConDias(["SABADO"])), [5])

    def test_la_vista_no_devuelve_error_500(self):
        camp = _campeonato_para_calendario("Web sin dias", self.datos["deporte"], [])
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4)
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(
            reverse("generar_fixture_campeonato", args=[camp.id]))
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(Partido.objects.filter(campeonato=camp).count(), 6)


class _ConDias:
    """Objeto minimo con dias_partido, para probar el helper sin tocar la BD."""

    def __init__(self, dias):
        self.dias_partido = dias

