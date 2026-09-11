"""CrearUsuarioArbitroForm: el formulario mas complejo de core/forms/arbitro.py.

Tenia 54% de cobertura real (medida con coverage): sus clean_* de
unicidad, la validacion de contraseñas y el save() transaccional (crea
Usuario + Arbitro + M2M de deportes) no tenian ningun test directo, solo
cobertura indirecta a traves de la vista GestionArbitroView.
"""

from core.tests.base import *  # noqa: F401,F403


class AltaDeArbitroPorFormulario(PruebaBase):

    CEDULA_A = "1105444176"
    CEDULA_B = "0102030400"  # otra cedula sintetica valida, distinta de la A

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _datos_validos(self, **extra):
        return {
            "username": "arbitro_nuevo", "email": "arbitro_nuevo@uide.edu.ec",
            "first_name": "Nuevo", "last_name": "Arbitro", "genero": "masculino",
            "cedula": self.CEDULA_A, "password": "Prueba.2026",
            "confirm_password": "Prueba.2026", "contacto": "099 123 4567",
            "experiencia": "3 años.", "deportes": [self.datos["deporte"].pk],
            "estado": True,
            **extra,
        }

    def test_formulario_valido_crea_usuario_y_arbitro(self):
        formulario = CrearUsuarioArbitroForm(data=self._datos_validos())
        self.assertTrue(formulario.is_valid(), formulario.errors.as_text())

        usuario = formulario.save()

        self.assertEqual(usuario.rol, "ARBITRO")
        self.assertTrue(usuario.check_password("Prueba.2026"))
        arbitro = Arbitro.objects.get(usuario=usuario)
        self.assertEqual(arbitro.contacto, "099 123 4567")
        self.assertIn(self.datos["deporte"], arbitro.deportes.all())

    def test_contrasenas_distintas_no_pasan(self):
        formulario = CrearUsuarioArbitroForm(
            data=self._datos_validos(confirm_password="Otra.2026"))
        self.assertFalse(formulario.is_valid())
        self.assertIn("confirm_password", formulario.errors)

    def test_username_duplicado_no_pasa(self):
        formulario = CrearUsuarioArbitroForm(
            data=self._datos_validos(username=self.datos["admin"].username))
        self.assertFalse(formulario.is_valid())
        self.assertIn("username", formulario.errors)

    def test_email_duplicado_no_pasa(self):
        formulario = CrearUsuarioArbitroForm(
            data=self._datos_validos(email=self.datos["admin"].email))
        self.assertFalse(formulario.is_valid())
        self.assertIn("email", formulario.errors)

    def test_cedula_duplicada_no_pasa(self):
        self.datos["admin"].cedula = self.CEDULA_A
        self.datos["admin"].save()
        formulario = CrearUsuarioArbitroForm(data=self._datos_validos())
        self.assertFalse(formulario.is_valid())
        self.assertIn("cedula", formulario.errors)

    def test_sin_deportes_no_pasa(self):
        """deportes es obligatorio: un arbitro sin deporte no se puede asignar."""
        formulario = CrearUsuarioArbitroForm(data=self._datos_validos(deportes=[]))
        self.assertFalse(formulario.is_valid())
        self.assertIn("deportes", formulario.errors)

    def test_dos_arbitros_con_cedulas_distintas_no_chocan(self):
        primero = CrearUsuarioArbitroForm(data=self._datos_validos())
        self.assertTrue(primero.is_valid(), primero.errors.as_text())
        primero.save()

        segundo = CrearUsuarioArbitroForm(data=self._datos_validos(
            username="arbitro_dos", email="dos@uide.edu.ec", cedula=self.CEDULA_B))
        self.assertTrue(segundo.is_valid(), segundo.errors.as_text())
