"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class BorradoDeEquipoExigePost(PruebaBase):
    """eliminar_equipo estaba registrado dos veces con nombres de argumento
    distintos; reverse() elegía la variante que la vista no acepta y el
    botón Eliminar respondía TypeError."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_get_no_borra_y_post_si(self):
        equipo = Equipo.objects.create(
            nombre="Equipo desechable", campeonato=self.datos["campeonato"],
            carrera=self.datos["carrera"], delegado=self.datos["delegado"])
        url = reverse("eliminar_equipo", kwargs={"id": equipo.pk})
        self.client.login(username="admin_test", password=PWD)

        self.client.get(url)
        self.assertTrue(Equipo.objects.filter(pk=equipo.pk).exists(),
                        "un GET no debe borrar el equipo")

        self.client.post(url)
        self.assertFalse(Equipo.objects.filter(pk=equipo.pk).exists(),
                         "un POST debe borrar el equipo")


class RegistroRenderizaTodosSusCampos(PruebaBase):
    """La plantilla de registro agrupa los campos por sección; si se añade
    uno al formulario debe seguir apareciendo."""

    def test_ningun_campo_queda_sin_renderizar(self):
        html = self.client.get(reverse("registro")).content.decode()
        for nombre in RegistroUsuarioForm().fields:
            with self.subTest(campo=nombre):
                self.assertIn(f'name="{nombre}"', html)

