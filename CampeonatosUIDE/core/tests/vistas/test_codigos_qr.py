"""CRUD de CodigoQR (codigoqr_views.py), sin ningun test propio (71% real)."""

import io

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from core.tests.base import *  # noqa: F401,F403


def _imagen():
    """PNG minimo pero real: ImageField valida con Pillow, no basta con
    bytes con cabecera de PNG a mano (Pillow los rechaza por corruptos)."""
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), color=(255, 0, 0)).save(buffer, format="PNG")
    return SimpleUploadedFile("qr.png", buffer.getvalue(), content_type="image/png")


class ListadoYBusquedaDeCodigosQr(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def setUp(self):
        self.client.force_login(self.datos["admin"])

    def test_solo_el_admin_puede_ver_el_listado(self):
        self.client.force_login(self.datos["delegado"])
        self.assertEqual(self.client.get(reverse("listar_codigos_qr")).status_code, 403)

    def test_sin_busqueda_lista_todos(self):
        respuesta = self.client.get(reverse("listar_codigos_qr"))
        self.assertEqual(list(respuesta.context["codigos_qr"]), list(CodigoQR.objects.all()))

    def test_la_busqueda_filtra_por_banco_o_descripcion(self):
        respuesta = self.client.get(reverse("listar_codigos_qr"), {"q": "Loja"})
        self.assertIn(CodigoQR.objects.first(), respuesta.context["codigos_qr"])
        respuesta_vacia = self.client.get(reverse("listar_codigos_qr"), {"q": "no-existe-esto"})
        self.assertEqual(list(respuesta_vacia.context["codigos_qr"]), [])


class AltaDeCodigoQr(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def setUp(self):
        self.client.force_login(self.datos["admin"])

    def _datos_qr(self, **extra):
        return {
            "banco": "Banco Nuevo", "numero_cuenta": "999999", "titular": "UIDE Nuevo",
            "tipo_cuenta": "AHORROS", "activo": True, "imagen_qr": _imagen(), **extra,
        }

    def test_post_valido_crea_el_codigo(self):
        respuesta = self.client.post(reverse("registrar_codigo_qr"), self._datos_qr())
        self.assertRedirects(respuesta, reverse("listar_codigos_qr"))
        self.assertTrue(CodigoQR.objects.filter(banco="Banco Nuevo").exists())

    def test_sin_imagen_no_es_valido(self):
        datos = self._datos_qr()
        del datos["imagen_qr"]
        antes = CodigoQR.objects.count()
        respuesta = self.client.post(reverse("registrar_codigo_qr"), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(CodigoQR.objects.count(), antes)

    def test_banco_y_cuenta_duplicados_no_pasan(self):
        existente = self.datos.get("campeonato").codigo_qr
        antes = CodigoQR.objects.count()
        respuesta = self.client.post(reverse("registrar_codigo_qr"), self._datos_qr(
            banco=existente.banco, numero_cuenta=existente.numero_cuenta))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(CodigoQR.objects.count(), antes)


class DetalleEdicionYBajaDeCodigoQr(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.qr = cls.datos["campeonato"].codigo_qr

    def setUp(self):
        self.client.force_login(self.datos["admin"])

    def test_detalle_responde_200(self):
        respuesta = self.client.get(reverse("detalle_codigo_qr", args=[self.qr.id]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["codigo"], self.qr)

    def test_editar_actualiza_el_titular(self):
        respuesta = self.client.post(
            reverse("editar_codigo_qr", args=[self.qr.id]),
            {"banco": self.qr.banco, "numero_cuenta": self.qr.numero_cuenta,
             "titular": "Nuevo Titular", "tipo_cuenta": self.qr.tipo_cuenta,
             "activo": True, "imagen_qr": _imagen()})
        self.assertRedirects(respuesta, reverse("listar_codigos_qr"))
        self.qr.refresh_from_db()
        self.assertEqual(self.qr.titular, "Nuevo Titular")

    def test_eliminar_lo_borra(self):
        respuesta = self.client.post(reverse("eliminar_codigo_qr", args=[self.qr.id]))
        self.assertRedirects(respuesta, reverse("listar_codigos_qr"))
        self.assertFalse(CodigoQR.objects.filter(pk=self.qr.id).exists())

    def test_un_delegado_no_puede_administrar_codigos_qr(self):
        self.client.force_login(self.datos["delegado"])
        self.assertEqual(
            self.client.get(reverse("detalle_codigo_qr", args=[self.qr.id])).status_code, 403)
        self.assertEqual(
            self.client.post(reverse("eliminar_codigo_qr", args=[self.qr.id])).status_code, 403)
        self.assertTrue(CodigoQR.objects.filter(pk=self.qr.id).exists())
