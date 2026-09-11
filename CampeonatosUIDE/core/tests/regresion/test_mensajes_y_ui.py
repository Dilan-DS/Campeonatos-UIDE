"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class LosMensajesNoSeDuplican(PruebaBase):
    """comun/base.html ya pinta los mensajes.

    Catorce plantillas repetian su propio bucle, asi que cada aviso salia
    dos veces; las que usaban is-{{ message.tags }} generaban is-error,
    que no existe en Bulma, y los errores quedaban sin recuadro.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_solo_base_recorre_los_mensajes(self):
        repiten = [
            ruta.relative_to(RAIZ_PLANTILLAS).as_posix()
            for ruta in sorted(RAIZ_PLANTILLAS.rglob("*.html"))
            if ruta.name != "base.html"
            and "for message in messages" in ruta.read_text(encoding="utf-8")
        ]
        self.assertEqual(repiten, [],
                         "plantillas que repiten el bucle de mensajes: " + ", ".join(repiten))

    def test_un_aviso_aparece_una_sola_vez(self):
        pago = Pago.objects.get(equipo=self.datos["equipo"])
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(
            reverse("aprobar_pago_admin", args=[pago.pk]),
            {"observacion_admin": "Comprobante correcto."}, follow=True)
        cuerpo = respuesta.content.decode()
        self.assertEqual(cuerpo.count("aprobado correctamente"), 1,
                         "el mensaje de exito no debe salir dos veces")

    def test_un_error_usa_is_danger_y_no_is_error(self):
        """El nivel ERROR de Django tiene el tag 'error', no 'danger'."""
        self.client.force_login(self.datos["delegado"])
        respuesta = self.client.get(reverse("listar_pagos_admin"), follow=True)
        cuerpo = respuesta.content.decode()
        self.assertNotIn("notification is-error", cuerpo,
                         "is-error no existe en Bulma: el aviso saldria sin recuadro")
        self.assertIn("notification is-danger", cuerpo)


class EtiquetaDeEstadoDePago(PruebaBase):
    """El elif comparaba una cadena literal, siempre verdadera.

    Cualquier pago que no estuviera APROBADO se pintaba de rojo como
    rechazado, incluidos los PENDIENTE.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.pago = Pago.objects.get(equipo=cls.datos["equipo"])

    def _color(self, estado):
        self.pago.estado = estado
        self.pago.save()
        self.client.force_login(self.datos["admin"])
        cuerpo = self.client.get(
            reverse("detalle_pago_admin", args=[self.pago.pk])).content.decode()
        for color in ("success", "danger", "warning"):
            if f'class="tag is-{color}"' in cuerpo:
                return color
        return None

    def test_cada_estado_con_su_color(self):
        self.assertEqual(self._color("APROBADO"), "success")
        self.assertEqual(self._color("RECHAZADO"), "danger")
        self.assertEqual(self._color("PENDIENTE"), "warning",
                         "un pago pendiente no debe pintarse como rechazado")

