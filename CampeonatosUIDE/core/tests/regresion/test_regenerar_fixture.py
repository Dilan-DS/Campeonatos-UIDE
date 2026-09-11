"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class RegenerarNoPierdeElCalendario(PruebaBase):
    """La vista borraba los partidos antes de generar y fuera de transaccion.

    Si la generacion fallaba, el campeonato se quedaba sin calendario:
    comprobado, 6 partidos programados pasaban a 0.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _camp_con_calendario(self):
        camp = _campeonato_para_calendario(
            "Regenerar", self.datos["deporte"], ["LUNES", "MIERCOLES"])
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4)
        self.client.force_login(self.datos["admin"])
        self.client.post(reverse("generar_fixture_campeonato", args=[camp.id]))
        return camp

    def test_si_no_se_generan_partidos_se_conserva_el_anterior(self):
        """Dos equipos aprobados pero de generos distintos.

        Asi se supera la guarda de "al menos 2 equipos aprobados" de la
        vista y se llega de verdad al borrado: cada genero se queda con un
        solo equipo, la generacion devuelve 0 y hay que revertir.
        """
        camp = self._camp_con_calendario()
        antes = Partido.objects.filter(campeonato=camp).count()
        self.assertEqual(antes, 6)

        Equipo.objects.filter(campeonato=camp).update(aprobado=False)
        _equipos_para_calendario(camp, self.datos["carrera"],
                                 self.datos["delegado"], 1, "masculino", "-bis")
        _equipos_para_calendario(camp, self.datos["carrera"],
                                 self.datos["delegado"], 1, "femenino", "-bis")
        self.assertEqual(
            Equipo.objects.filter(campeonato=camp, aprobado=True).count(), 2,
            "la vista debe pasar su guarda previa y llegar al borrado")

        respuesta = self.client.post(
            reverse("generar_fixture_campeonato", args=[camp.id]))
        self.assertEqual(respuesta.status_code, 302)

        self.assertEqual(Partido.objects.filter(campeonato=camp).count(), antes,
                         "el calendario anterior no debe perderse")

    def test_regenerar_bien_sustituye_el_calendario(self):
        """El caso normal debe seguir funcionando."""
        camp = self._camp_con_calendario()
        ids_antes = set(Partido.objects.filter(campeonato=camp).values_list("id", flat=True))
        self.client.post(reverse("generar_fixture_campeonato", args=[camp.id]))
        ids_despues = set(Partido.objects.filter(campeonato=camp).values_list("id", flat=True))
        self.assertEqual(len(ids_despues), 6)
        self.assertFalse(ids_antes & ids_despues, "deben ser partidos nuevos")

