"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class CedulaEnLosFormularios(PruebaBase):
    """La validacion se aplica en cada punto de entrada real.

    Se comprueba formulario a formulario, no solo el validador suelto: es
    donde llegan los datos del usuario.
    """

    CEDULA_VALIDA = "1105444176"
    CEDULA_INVALIDA = "1105444177"

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _registro(self, cedula):
        return RegistroUsuarioForm(data={
            "username": "aspirante", "first_name": "Ana", "last_name": "Lopez",
            "email": "aspirante@uide.edu.ec", "cedula": cedula,
            "genero": "masculino", "rol": "JUGADOR",
            "password1": "Prueba.2026", "password2": "Prueba.2026",
        })

    def test_el_registro_publico_rechaza_una_cedula_inventada(self):
        formulario = self._registro(self.CEDULA_INVALIDA)
        self.assertFalse(formulario.is_valid())
        self.assertIn("cedula", formulario.errors)

    def test_el_registro_publico_acepta_una_valida_no_almacenada(self):
        self.assertFalse(Usuario.objects.filter(cedula=self.CEDULA_VALIDA).exists())
        formulario = self._registro(self.CEDULA_VALIDA)
        self.assertTrue(formulario.is_valid(), formulario.errors.as_text())

    def test_el_perfil_rechaza_una_cedula_inventada(self):
        formulario = PerfilUsuarioForm(
            instance=self.datos["jugador"].usuario,
            data={"first_name": "A", "last_name": "B", "email": "p@uide.edu.ec",
                  "cedula": self.CEDULA_INVALIDA, "genero": "masculino",
                  "carrera": self.datos["carrera"].pk})
        self.assertFalse(formulario.is_valid())
        self.assertIn("cedula", formulario.errors)

    def test_el_formulario_de_usuario_rechaza_aunque_no_declare_validador(self):
        """UsuarioForm no declara el validador: lo hereda del campo del modelo."""
        formulario = UsuarioForm(data={"username": "otro", "email": "o@uide.edu.ec",
                                       "cedula": self.CEDULA_INVALIDA, "rol": "JUGADOR"})
        self.assertFalse(formulario.is_valid())
        self.assertIn("cedula", formulario.errors)

    def test_el_alta_de_arbitro_rechaza_una_cedula_inventada(self):
        formulario = ArbitroForm(data={
            "username": "arb_nuevo", "email": "arb@uide.edu.ec",
            "first_name": "A", "last_name": "B", "genero": "masculino",
            "is_active": True, "cedula": self.CEDULA_INVALIDA})
        self.assertFalse(formulario.is_valid())
        self.assertIn("cedula", formulario.errors)

    def test_dos_arbitros_sin_cedula_no_chocan(self):
        base = {"first_name": "A", "last_name": "B", "genero": "masculino",
                "is_active": True, "cedula": ""}
        primero = ArbitroForm(data={**base, "username": "arb_uno",
                                    "email": "uno@uide.edu.ec"})
        self.assertTrue(primero.is_valid(), primero.errors.as_text())
        creado = primero.save()
        self.assertIsNone(creado.cedula, "sin cedula debe guardarse NULL, no ''")

        segundo = ArbitroForm(data={**base, "username": "arb_dos",
                                    "email": "dos@uide.edu.ec"})
        self.assertTrue(segundo.is_valid(),
                        f"el segundo arbitro sin cedula no debe chocar: "
                        f"{segundo.errors.as_text()}")


class CedulaNoSePuedeSaltarPorHttp(PruebaBase):
    """El backend es la autoridad: no vale con la validacion del navegador.

    Se envia un POST directo al endpoint de registro, como haria curl,
    saltandose cualquier comprobacion del formulario en el cliente.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_un_post_directo_con_cedula_inventada_no_crea_usuario(self):
        antes = Usuario.objects.count()
        respuesta = self.client.post(reverse("registro"), {
            "username": "colado", "first_name": "Ana", "last_name": "Lopez",
            "email": "colado@uide.edu.ec", "cedula": "1105444177",
            "genero": "masculino", "rol": "JUGADOR",
            "password1": "Prueba.2026", "password2": "Prueba.2026",
        })
        self.assertEqual(Usuario.objects.count(), antes,
                         "una cedula que no cumple el algoritmo no debe crear usuario")
        self.assertFalse(Usuario.objects.filter(username="colado").exists())
        self.assertEqual(respuesta.status_code, 200)

    def test_un_post_directo_con_cedula_valida_si_crea_usuario(self):
        respuesta = self.client.post(reverse("registro"), {
            "username": "correcto", "first_name": "Ana", "last_name": "Lopez",
            "email": "correcto@uide.edu.ec", "cedula": "1105444176",
            "genero": "masculino", "rol": "JUGADOR",
            "password1": "Prueba.2026", "password2": "Prueba.2026",
        }, follow=True)
        self.assertTrue(Usuario.objects.filter(username="correcto").exists(),
                        f"deberia haberse creado: {respuesta.status_code}")

