"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class AprobacionDePagosRespetaRolYEstado(PruebaBase):
    """Quien puede aprobar un pago y desde que estado.

    Aprobar es lo que habilita a un equipo, asi que la vista solo debe
    aceptar ADMIN y solo debe mover un pago que este PENDIENTE.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.pago = Pago.objects.get(equipo=cls.datos["equipo"])

    def _aprobar(self, usuario):
        self.client.force_login(usuario)
        return self.client.post(
            reverse("aprobar_pago_admin", args=[self.pago.pk]),
            {"observacion_admin": "Comprobante correcto."})

    def test_el_admin_aprueba_un_pago_pendiente(self):
        self._aprobar(self.datos["admin"])
        self.pago.refresh_from_db()
        self.assertEqual(self.pago.estado, "APROBADO")
        self.assertEqual(self.pago.observacion_admin, "Comprobante correcto.")

    def test_el_delegado_no_puede_aprobar_su_propio_pago(self):
        self._aprobar(self.datos["delegado"])
        self.pago.refresh_from_db()
        self.assertEqual(self.pago.estado, "PENDIENTE",
                         "solo ADMIN debe poder aprobar un pago")

    def test_no_reaprueba_un_pago_ya_rechazado(self):
        self.pago.estado = "RECHAZADO"
        self.pago.save()
        self._aprobar(self.datos["admin"])
        self.pago.refresh_from_db()
        self.assertEqual(self.pago.estado, "RECHAZADO",
                         "aprobar solo debe actuar sobre pagos PENDIENTE")

    def test_aprobar_por_get_no_cambia_nada(self):
        """La aprobacion solo esta implementada en POST."""
        self.client.force_login(self.datos["admin"])
        self.client.get(reverse("aprobar_pago_admin", args=[self.pago.pk]))
        self.pago.refresh_from_db()
        self.assertEqual(self.pago.estado, "PENDIENTE")

    def test_el_delegado_solo_ve_los_pagos_de_sus_equipos(self):
        ajeno = Usuario.objects.create_user(
            username="delegado_ajeno", email="delegado_ajeno@uide.edu.ec",
            password=PWD, rol="DELEGADO", carrera=self.datos["carrera"],
            genero="masculino")
        self.client.force_login(ajeno)
        respuesta = self.client.get(reverse("mis_pagos_delegado"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(list(respuesta.context["pagos"]), [],
                         "un delegado no debe ver pagos de equipos que no son suyos")


class PagoDeOtroEquipoEsInaccesible(PruebaBase):
    """IDOR: el equipo llegaba por la URL sin comprobar de quien era.

    La restriccion por queryset del formulario solo se aplicaba al rol
    DELEGADO, asi que un JUGADOR o un ARBITRO podian abrir y modificar el
    pago de cualquier equipo. Comprobado explotable antes del arreglo.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.equipo = cls.datos["equipo"]
        cls.pago = Pago.objects.get(equipo=cls.equipo)

    def _url(self):
        return reverse("registrar_pago_equipo", args=[self.equipo.pk])

    def test_un_jugador_no_puede_abrirlo(self):
        self.client.force_login(self.datos["jugador"].usuario)
        self.assertEqual(self.client.get(self._url()).status_code, 403)

    def test_un_arbitro_no_puede_abrirlo(self):
        self.client.force_login(self.datos["arbitro"].usuario)
        self.assertEqual(self.client.get(self._url()).status_code, 403)

    def test_un_jugador_no_puede_modificarlo(self):
        self.client.force_login(self.datos["jugador"].usuario)
        antes = self.pago.metodo
        self.client.post(self._url(), {"equipo": str(self.equipo.pk), "metodo": "EFECTIVO"})
        self.pago.refresh_from_db()
        self.assertEqual(self.pago.metodo, antes,
                         "un jugador no debe poder cambiar el pago de un equipo")

    def test_un_delegado_ajeno_no_puede(self):
        ajeno = Usuario.objects.create_user(
            username="delegado_ajeno_pago", email="dap@uide.edu.ec", password=PWD,
            rol="DELEGADO", carrera=self.datos["carrera"], genero="masculino")
        self.client.force_login(ajeno)
        self.assertEqual(self.client.get(self._url()).status_code, 403)

    def test_el_delegado_del_equipo_si_puede(self):
        """El arreglo no debe romper el flujo normal del delegado."""
        self.client.force_login(self.datos["delegado"])
        self.assertEqual(self.client.get(self._url()).status_code, 200)

    def test_el_admin_puede_con_cualquier_equipo(self):
        self.client.force_login(self.datos["admin"])
        self.assertEqual(self.client.get(self._url()).status_code, 200)

