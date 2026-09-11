"""Reglas reales de pago_views.py que no tenian test propio.

RechazarPagoAdminView, el flujo POST completo de RegistrarPagoDelegadoView
(auto-asignacion del QR principal en transferencias, limpieza del QR en
efectivo), DetallePagoDelegadoView, EliminarPagoDelegadoView y
CambiarEstadoPagoAdminView estaban entre 49% y 71% de cobertura real.
"""

from core.tests.base import *  # noqa: F401,F403


class RechazoDePagos(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.pago = Pago.objects.get(equipo=cls.datos["equipo"])

    def _rechazar(self, usuario):
        self.client.force_login(usuario)
        return self.client.post(
            reverse("rechazar_pago_admin", args=[self.pago.pk]),
            {"observacion_admin": "Comprobante ilegible."})

    def test_el_admin_rechaza_un_pago_pendiente(self):
        self._rechazar(self.datos["admin"])
        self.pago.refresh_from_db()
        self.assertEqual(self.pago.estado, "RECHAZADO")
        self.assertEqual(self.pago.observacion_admin, "Comprobante ilegible.")

    def test_el_admin_tambien_puede_rechazar_uno_ya_aprobado(self):
        self.pago.estado = "APROBADO"
        self.pago.save()
        self._rechazar(self.datos["admin"])
        self.pago.refresh_from_db()
        self.assertEqual(self.pago.estado, "RECHAZADO")

    def test_no_se_puede_rechazar_dos_veces_sin_cambiar_nada(self):
        self.pago.estado = "RECHAZADO"
        self.pago.save()
        self._rechazar(self.datos["admin"])
        self.pago.refresh_from_db()
        self.assertEqual(self.pago.estado, "RECHAZADO")

    def test_un_delegado_no_puede_rechazar(self):
        self._rechazar(self.datos["delegado"])
        self.pago.refresh_from_db()
        self.assertEqual(self.pago.estado, "PENDIENTE")


class RegistroDePagoPorDelegado(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def setUp(self):
        self.client.force_login(self.datos["delegado"])

    def test_transferencia_sin_qr_toma_el_principal_automaticamente(self):
        respuesta = self.client.post(
            reverse("registrar_pago_equipo", args=[self.datos["equipo"].pk]),
            {"equipo": self.datos["equipo"].pk, "metodo": "TRANSFERENCIA"})
        pago = Pago.objects.get(equipo=self.datos["equipo"])
        self.assertEqual(pago.metodo, "TRANSFERENCIA")
        self.assertEqual(pago.codigo_qr_id, CodigoQR.objects.get(es_principal=True).pk)
        self.assertRedirects(respuesta, reverse("detalle_pago_delegado"))

    def test_efectivo_limpia_el_codigo_qr(self):
        pago = Pago.objects.get(equipo=self.datos["equipo"])
        pago.metodo = "TRANSFERENCIA"
        pago.codigo_qr = CodigoQR.objects.first()
        pago.save()

        self.client.post(
            reverse("registrar_pago_equipo", args=[self.datos["equipo"].pk]),
            {"equipo": self.datos["equipo"].pk, "metodo": "EFECTIVO"})

        pago.refresh_from_db()
        self.assertEqual(pago.metodo, "EFECTIVO")
        self.assertIsNone(pago.codigo_qr_id)

    def test_actualiza_el_pago_existente_en_vez_de_duplicarlo(self):
        antes = Pago.objects.filter(equipo=self.datos["equipo"]).count()
        self.client.post(
            reverse("registrar_pago_equipo", args=[self.datos["equipo"].pk]),
            {"equipo": self.datos["equipo"].pk, "metodo": "EFECTIVO"})
        despues = Pago.objects.filter(equipo=self.datos["equipo"]).count()
        self.assertEqual(antes, despues, "debe actualizar el pago unico del equipo, no crear otro")


class DetalleYBajaDePagoDelDelegado(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.pago = Pago.objects.get(equipo=cls.datos["equipo"])

    def setUp(self):
        self.client.force_login(self.datos["delegado"])

    def test_detalle_redirige_si_no_hay_pago_para_el_campeonato(self):
        Pago.objects.filter(equipo=self.datos["equipo"]).delete()
        respuesta = self.client.get(
            reverse("detalle_pago_delegado"), {"campeonato_id": self.datos["campeonato"].id})
        self.assertRedirects(
            respuesta,
            reverse("registrar_pago_delegado") + f"?campeonato_id={self.datos['campeonato'].id}")

    def test_detalle_redirige_al_dashboard_si_no_tiene_equipo_en_ese_campeonato(self):
        otro_campeonato = _campeonato_para_calendario(
            "Sin equipo del delegado", self.datos["deporte"], ["LUNES"])
        respuesta = self.client.get(
            reverse("detalle_pago_delegado"), {"campeonato_id": otro_campeonato.id})
        self.assertRedirects(respuesta, reverse("delegado_dashboard"))

    def test_un_delegado_no_puede_eliminar_el_pago_de_otro_equipo(self):
        otro_delegado = Usuario.objects.create_user(
            username="delegado_ajeno_baja", email="dab@uide.edu.ec", password=PWD,
            rol="DELEGADO", carrera=self.datos["carrera"], genero="masculino")
        self.client.force_login(otro_delegado)
        otro_equipo = Equipo.objects.create(
            nombre="Equipo del otro", campeonato=self.datos["campeonato"],
            carrera=self.datos["carrera"], delegado=otro_delegado, aprobado=True)
        self.client.post(
            reverse("eliminar_pago_delegado", args=[self.pago.pk]),
            {"campeonato_id": self.datos["campeonato"].id})
        self.assertTrue(Pago.objects.filter(pk=self.pago.pk).exists(),
                        "no debe poder borrar el pago de un equipo ajeno")

    def test_el_delegado_del_equipo_si_puede_eliminar_su_pago(self):
        self.client.post(
            reverse("eliminar_pago_delegado", args=[self.pago.pk]),
            {"campeonato_id": self.datos["campeonato"].id})
        self.assertFalse(Pago.objects.filter(pk=self.pago.pk).exists())


class RegistroDirectoDePagoPorAdmin(PruebaBase):
    """RegistrarPagoAdminView / EditarPagoAdminView / EliminarPagoAdminView.

    Es el alta manual de un pago sin pasar por el flujo del delegado
    (metodo=EFECTIVO, sin comprobante ni QR obligatorios).
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def setUp(self):
        self.client.force_login(self.datos["admin"])

    def _datos_pago(self, equipo, **extra):
        return {
            "equipo": equipo.pk, "metodo": "EFECTIVO", "estado": "PENDIENTE",
            **extra,
        }

    def test_un_delegado_no_puede_registrar_un_pago_directo(self):
        otro_equipo = Equipo.objects.create(
            nombre="Otro equipo", campeonato=self.datos["campeonato"],
            carrera=self.datos["carrera"], delegado=self.datos["delegado"], aprobado=True)
        self.client.force_login(self.datos["delegado"])
        self.client.post(reverse("registrar_pago_admin"), self._datos_pago(otro_equipo))
        self.assertFalse(Pago.objects.filter(equipo=otro_equipo).exists())

    def test_el_admin_registra_un_pago_para_un_equipo_sin_pago_previo(self):
        equipo_sin_pago = Equipo.objects.create(
            nombre="Sin pago previo", campeonato=self.datos["campeonato"],
            carrera=self.datos["carrera"], delegado=self.datos["delegado"], aprobado=True)
        respuesta = self.client.post(
            reverse("registrar_pago_admin"), self._datos_pago(equipo_sin_pago))
        self.assertRedirects(respuesta, reverse("listar_pagos_admin"))
        self.assertTrue(Pago.objects.filter(equipo=equipo_sin_pago).exists())

    def test_el_admin_edita_un_pago_existente(self):
        pago = Pago.objects.get(equipo=self.datos["equipo"])
        respuesta = self.client.post(
            reverse("editar_pago_admin", args=[pago.pk]),
            self._datos_pago(self.datos["equipo"], estado="APROBADO"))
        self.assertRedirects(respuesta, reverse("listar_pagos_admin"))
        pago.refresh_from_db()
        self.assertEqual(pago.estado, "APROBADO")

    def test_el_admin_elimina_un_pago(self):
        pago = Pago.objects.get(equipo=self.datos["equipo"])
        respuesta = self.client.post(reverse("eliminar_pago_admin", args=[pago.pk]))
        self.assertRedirects(respuesta, reverse("listar_pagos_admin"))
        self.assertFalse(Pago.objects.filter(pk=pago.pk).exists())

    def test_un_delegado_no_puede_eliminar_desde_la_vista_de_admin(self):
        pago = Pago.objects.get(equipo=self.datos["equipo"])
        self.client.force_login(self.datos["delegado"])
        self.client.post(reverse("eliminar_pago_admin", args=[pago.pk]))
        self.assertTrue(Pago.objects.filter(pk=pago.pk).exists())


class CambioDeEstadoDePagoPorAdmin(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.pago = Pago.objects.get(equipo=cls.datos["equipo"])

    def _cambiar(self, usuario, estado, **extra):
        self.client.force_login(usuario)
        return self.client.post(
            reverse("cambiar_estado_pago_admin", args=[self.pago.pk]),
            {"estado": estado, **extra})

    def test_un_estado_no_valido_no_se_aplica(self):
        self._cambiar(self.datos["admin"], "ESTADO_INVENTADO")
        self.pago.refresh_from_db()
        self.assertEqual(self.pago.estado, "PENDIENTE")

    def test_cambia_a_cualquiera_de_los_tres_estados_validos(self):
        for estado in ("APROBADO", "RECHAZADO", "PENDIENTE"):
            with self.subTest(estado=estado):
                self._cambiar(self.datos["admin"], estado)
                self.pago.refresh_from_db()
                self.assertEqual(self.pago.estado, estado)

    def test_redirige_al_next_si_se_indica(self):
        destino = reverse("listar_pagos_admin")
        respuesta = self._cambiar(self.datos["admin"], "APROBADO", next=destino)
        self.assertRedirects(respuesta, destino)

    def test_un_delegado_no_puede_cambiar_el_estado(self):
        self._cambiar(self.datos["delegado"], "APROBADO")
        self.pago.refresh_from_db()
        self.assertEqual(self.pago.estado, "PENDIENTE")

    def test_reenviar_el_mismo_estado_no_pisa_la_observacion(self):
        self.pago.observacion_admin = "Motivo original."
        self.pago.save()
        self._cambiar(self.datos["admin"], "PENDIENTE", observacion_admin="Otra cosa")
        self.pago.refresh_from_db()
        self.assertEqual(self.pago.observacion_admin, "Motivo original.",
                         "sin cambio de estado no debe tocar la observacion")


class ListadoPaginadoDePagosDelDelegado(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_un_campeonato_id_no_numerico_se_ignora_sin_reventar(self):
        self.client.force_login(self.datos["delegado"])
        respuesta = self.client.get(
            reverse("mis_pagos_delegado"), {"campeonato_id": "no-es-un-numero"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.context["pagos"]), 1)
