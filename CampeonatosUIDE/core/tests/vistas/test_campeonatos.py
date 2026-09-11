"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class VisibilidadPublicaDeCampeonatos(PruebaBase):
    """es_publico es 'SI'/'NO': no puede evaluarse como booleano.

    La plantilla filtraba con `{% if campeonato.es_publico %}`, cierto
    también para 'NO', y publicaba campeonatos marcados como no públicos.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.privado = Campeonato.objects.create(
            nombre="Campeonato privado", tipo_campeonato="LIGA",
            deporte=cls.datos["deporte"], descripcion="No debe publicarse.",
            fecha_inicio=date.today(), fecha_fin=date.today() + timedelta(days=5),
            estado="EN_CURSO", activo="SI", es_publico="NO")

    def test_no_publico_no_aparece(self):
        html = self.client.get(reverse("campeonatos_publicos")).content.decode()
        self.assertIn("Copa de prueba", html)
        self.assertNotIn("Campeonato privado", html)

    def test_portada_solo_publica_los_publicos(self):
        html = self.client.get(reverse("inicio_publico")).content.decode()
        self.assertNotIn("Campeonato privado", html)


class PortadaMuestraDatos(PruebaBase):
    """La portada se renderizaba sin contexto y mostraba siempre sus estados
    vacíos, aunque hubiera campeonatos, partidos y noticias."""

    @classmethod
    def setUpTestData(cls):
        _datos_base()

    def test_portada_incluye_datos_reales(self):
        respuesta = self.client.get(reverse("inicio_publico"))
        self.assertEqual(respuesta.status_code, 200)
        for clave in ("campeonatos", "proximos_partidos", "noticias", "testimonios"):
            self.assertIn(clave, respuesta.context, f"falta {clave} en el contexto")
        self.assertContains(respuesta, "Copa de prueba")
        self.assertNotContains(respuesta, "No hay campeonatos activos")


class PanelAdminMuestraMetricas(PruebaBase):
    """El panel se renderizaba sin contexto y las cuatro métricas salían
    como un guion."""

    @classmethod
    def setUpTestData(cls):
        _datos_base()

    def test_metricas_con_valores(self):
        self.client.login(username="admin_test", password=PWD)
        respuesta = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(respuesta.status_code, 200)
        for clave in ("kpi_usuarios", "kpi_campeonatos", "kpi_equipos", "kpi_arbitros"):
            self.assertIsInstance(respuesta.context[clave], int)
        self.assertEqual(respuesta.context["kpi_equipos"], Equipo.objects.count())

