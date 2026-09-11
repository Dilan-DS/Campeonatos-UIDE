"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class ContratoDelActaDelArbitro(PruebaBase):
    """ArbitroActaForm perdió su __init__ al migrar los formularios y la
    carga del acta respondía TypeError: ninguna acta podía registrarse."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_el_formulario_acepta_los_jugadores(self):
        jugadores = Jugador.objects.filter(equipo=self.datos["equipo"])
        form = ArbitroActaForm(jugadores_local=jugadores, jugadores_visitante=[])
        for j in jugadores:
            for prefijo in ("goles", "amarillas", "roja", "susp", "susp_ini",
                            "susp_fin", "susp_mot"):
                self.assertIn(f"{prefijo}_{j.id}", form.fields)
        for campo in ("resultado_local", "resultado_visitante", "observaciones",
                      "tarjetas_amarillas_local", "tarjetas_rojas_visitante"):
            self.assertIn(campo, form.fields)

    def test_el_acta_carga_y_guarda(self):
        partido = self.datos["partido"]
        self.client.login(username="arbitro_test", password=PWD)
        url = reverse("acta_partido_arbitro", kwargs={"pk": partido.pk})
        self.assertEqual(self.client.get(url).status_code, 200)

        jugador = Jugador.objects.filter(equipo=partido.equipo_local).first()
        datos = {"resultado_local": 1, "resultado_visitante": 0,
                 "tarjetas_amarillas_local": 0, "tarjetas_amarillas_visitante": 0,
                 "tarjetas_rojas_local": 0, "tarjetas_rojas_visitante": 0,
                 "observaciones": "Sin incidencias.", f"goles_{jugador.id}": 1}
        self.client.post(url, datos)
        partido.refresh_from_db()
        self.assertEqual(partido.resultado_local, 1)
        self.assertEqual(partido.estado, "FINALIZADO")

    def test_rechaza_goles_que_no_cuadran(self):
        partido = self.datos["partido"]
        self.client.login(username="arbitro_test", password=PWD)
        url = reverse("acta_partido_arbitro", kwargs={"pk": partido.pk})
        self.client.post(url, {"resultado_local": 3, "resultado_visitante": 0,
                               "observaciones": ""})
        partido.refresh_from_db()
        self.assertIsNone(partido.resultado_local)
        self.assertEqual(partido.estado, "PROGRAMADO")

