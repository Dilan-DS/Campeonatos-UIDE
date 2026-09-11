"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class CamposRenombradosPorMigracion0003(PruebaBase):
    """Las vistas deben ordenar por los nombres nuevos, no por los antiguos.

    galeria, noticias y testimonios ordenaban por 'fecha' y
    'fecha_publicacion' después de que la migración 0003 los renombrara a
    'creado_en', y las tres respondían FieldError.
    """

    @classmethod
    def setUpTestData(cls):
        _datos_base()

    def test_listados_de_contenido_responden(self):
        for nombre in ("listar_imagenes_galeria", "listar_noticias", "listar_testimonios"):
            with self.subTest(ruta=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)

