"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class ExportacionesDeEstadisticas(PruebaBase):
    """Las exportaciones leían un campo 'asistencias' que sólo existe en el
    modelo de básquet y respondían AttributeError."""

    @classmethod
    def setUpTestData(cls):
        _datos_base()

    def test_pdf_y_excel_se_generan(self):
        self.client.login(username="admin_test", password=PWD)
        for nombre in ("exportar_estadisticas_pdf", "exportar_estadisticas_excel"):
            with self.subTest(ruta=nombre):
                respuesta = self.client.get(reverse(nombre))
                self.assertEqual(respuesta.status_code, 200)
                self.assertTrue(respuesta["Content-Disposition"].startswith("attachment"))


class EstadisticasDeCadaDeporteUsanCamposQueExisten(PruebaBase):
    """Ajedrez y videojuegos pedian stat.partidas_jugadas, inexistente.

    El campo de esos modelos es partidos_jugados, asi que la columna
    "Partidas jugadas" salia siempre vacia.
    """

    def test_los_campos_declarados_existen_en_su_modelo(self):
        from core.views.estadisticas_views import DEPORTES_CON_ESTADISTICA
        for deporte, modelo, columnas in DEPORTES_CON_ESTADISTICA:
            nombres = {f.name for f in modelo._meta.get_fields() if f.concrete}
            for etiqueta, campo in columnas:
                with self.subTest(deporte=deporte, campo=campo):
                    self.assertIn(campo, nombres,
                                  f"{modelo.__name__} no tiene {campo}")

    def test_las_plantillas_por_deporte_no_dejan_celdas_vacias(self):
        from django.template.loader import render_to_string

        class Camp:
            nombre = "Copa de prueba"

        class Us:
            username = "jugador1"

        class Eq:
            nombre = "Titanes TI"

        class Jug:
            usuario = Us()
            equipo = Eq()

        class Stat:
            jugador = Jug()
            campeonato = Camp()
            partidos_jugados = 7
            goles = 3
            tarjetas_amarillas = 1
            tarjetas_rojas = 0
            canastas = 22
            rebotes = 9
            asistencias = 4
            partidas_ganadas = 5
            partidas_empatadas = 1
            partidas_perdidas = 1
            sets_ganados = 6
            sets_perdidos = 2
            partidos_ganados = 4
            partidos_perdidos = 3

        contexto = {"estadisticas": [Stat()], "campeonatos": [],
                    "selected_campeonato_id": None}
        for deporte in ("futbol", "basquet", "ajedrez", "ecuaboly",
                        "pingpong", "tenis", "futbolin", "videojuegos"):
            with self.subTest(deporte=deporte):
                html = render_to_string(
                    f"estadisticas/estadisticas_{deporte}.html", contexto)
                self.assertNotIn("<td></td>", html,
                                 "ninguna columna debe quedar vacia")
                self.assertNotIn("None", html)


# ---------------------------------------------------------------------------
# Control de acceso.
#
# Cada clase fija una vulnerabilidad que se comprobo explotable en la
# auditoria, y comprueba tambien que el uso legitimo sigue funcionando:
# cerrar un agujero sin dejar fuera a quien si tiene derecho.
# ---------------------------------------------------------------------------

