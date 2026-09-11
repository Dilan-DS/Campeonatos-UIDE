"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class ElComandoDeCalendarioArranca(PruebaBase):
    """Importaba asignar_arbitros_a_partidos, que no existe en el proyecto.

    El comando aparecia en `manage.py help` pero fallaba con ImportError
    antes de ejecutar nada.
    """

    def test_el_modulo_se_importa(self):
        from core.management.commands import generar_fixtures  # noqa: F401

    def test_el_comando_se_ejecuta_sin_campeonatos_pendientes(self):
        from io import StringIO
        from django.core.management import call_command

        salida = StringIO()
        call_command("generar_fixtures", stdout=salida, stderr=StringIO())
        self.assertIn("No hay campeonatos", salida.getvalue())

    def test_el_comando_genera_el_calendario_de_punta_a_punta(self):
        """Campeonato con la inscripcion cerrada: el comando debe programarlo."""
        from io import StringIO
        from django.core.management import call_command

        datos = _datos_base()
        camp = _campeonato_para_calendario(
            "Comando liga", datos["deporte"], ["LUNES", "MIERCOLES"])
        camp.fecha_fin_inscripcion = date.today() - timedelta(days=1)
        camp.fixture_generado = False
        camp.estado = "INSCRIPCION"
        camp.save()
        _equipos_para_calendario(camp, datos["carrera"], datos["delegado"], 4)

        salida = StringIO()
        call_command("generar_fixtures", stdout=salida, stderr=StringIO())

        camp.refresh_from_db()
        self.assertEqual(Partido.objects.filter(campeonato=camp).count(), 6)
        self.assertTrue(camp.fixture_generado)
        self.assertEqual(camp.estado, "EN_CURSO")
        self.assertIn("finalizado", salida.getvalue())

