"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class CatalogoQrSeSerializaEscapado(PruebaBase):
    """El catalogo iba con json.dumps y |safe dentro de un <script>.

    json.dumps no escapa < ni >, asi que un "</script>" en cualquier campo
    del QR (banco, titular, numero de cuenta) cerraba el bloque y el resto
    se interpretaba como HTML: XSS almacenado contra los delegados.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_una_carga_en_el_banco_no_rompe_el_script(self):
        qr = CodigoQR.objects.first()
        qr.banco = '</script><img src=x onerror=alert(1)>'
        qr.save()

        self.client.force_login(self.datos["delegado"])
        respuesta = self.client.get(
            reverse("registrar_pago_equipo", args=[self.datos["equipo"].pk]))
        self.assertEqual(respuesta.status_code, 200)
        cuerpo = respuesta.content.decode()

        self.assertNotIn("</script><img", cuerpo,
                         "la carga no debe salir literal y cerrar el <script>")
        self.assertIn("\\u003C", cuerpo,
                      "json_script debe escapar el < como \\u003C")

