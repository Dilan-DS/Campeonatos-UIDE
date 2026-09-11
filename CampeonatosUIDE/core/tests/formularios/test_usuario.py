"""Formularios de core/forms/usuario.py sin cobertura directa.

CrearUsuarioDelegadoForm.save(), las ramas de duplicado de
PerfilUsuarioForm (cedula/email ya usados por OTRO usuario, pero no por
uno mismo) y las dos ramas de PasswordResetConValidacionForm.clean_email
estaban entre el 74% de cobertura real de este archivo.
"""

from core.tests.base import *  # noqa: F401,F403


class AltaDeDelegadoPorFormulario(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_guarda_con_password_hasheada_y_rol_delegado(self):
        formulario = CrearUsuarioDelegadoForm(data={
            "username": "delegado_nuevo", "first_name": "Nuevo", "last_name": "Delegado",
            "email": "delegado_nuevo@uide.edu.ec", "carrera": self.datos["carrera"].pk,
            "password": "Prueba.2026", "password2": "Prueba.2026",
        })
        self.assertTrue(formulario.is_valid(), formulario.errors.as_text())

        usuario = formulario.save()

        self.assertEqual(usuario.rol, "DELEGADO")
        self.assertTrue(usuario.check_password("Prueba.2026"))
        self.assertNotEqual(usuario.password, "Prueba.2026", "no debe guardarse en texto plano")

    def test_rechaza_si_las_contrasenas_no_coinciden(self):
        formulario = CrearUsuarioDelegadoForm(data={
            "username": "delegado_typo", "email": "delegado_typo@uide.edu.ec",
            "password": "Prueba.2026", "password2": "Prueba.2027",
        })
        self.assertFalse(formulario.is_valid())
        self.assertIn("password2", formulario.errors)

    def test_rechaza_un_correo_ya_registrado(self):
        formulario = CrearUsuarioDelegadoForm(data={
            "username": "otro_delegado", "email": self.datos["admin"].email,
            "password": "Prueba.2026", "password2": "Prueba.2026",
        })
        self.assertFalse(formulario.is_valid())
        self.assertIn("email", formulario.errors)

    def test_nombre_apellido_y_carrera_son_opcionales(self):
        formulario = CrearUsuarioDelegadoForm(data={
            "username": "delegado_minimo", "email": "delegado_minimo@uide.edu.ec",
            "password": "Prueba.2026", "password2": "Prueba.2026",
        })
        self.assertTrue(formulario.is_valid(), formulario.errors.as_text())


class EdicionDePerfilPropio(PruebaBase):
    """PerfilUsuarioForm excluye la propia instancia al chequear duplicados."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _formulario(self, usuario, **overrides):
        datos = {
            "first_name": usuario.first_name or "Nombre",
            "last_name": usuario.last_name or "Apellido",
            "email": usuario.email,
            "cedula": usuario.cedula or "1105444176",
            "genero": "masculino",
            "carrera": self.datos["carrera"].pk,
        }
        datos.update(overrides)
        return PerfilUsuarioForm(instance=usuario, data=datos)

    def test_reenviar_el_propio_email_y_cedula_no_es_un_duplicado(self):
        self.datos["delegado"].cedula = "1105444176"
        self.datos["delegado"].save()
        formulario = self._formulario(self.datos["delegado"])
        self.assertTrue(formulario.is_valid(), formulario.errors.as_text())

    def test_no_puede_tomar_el_email_de_otro_usuario(self):
        formulario = self._formulario(
            self.datos["delegado"], email=self.datos["admin"].email)
        self.assertFalse(formulario.is_valid())
        self.assertIn("email", formulario.errors)

    def test_no_puede_tomar_la_cedula_de_otro_usuario(self):
        self.datos["admin"].cedula = "1105444176"
        self.datos["admin"].save()
        formulario = self._formulario(self.datos["delegado"], cedula="1105444176")
        self.assertFalse(formulario.is_valid())
        self.assertIn("cedula", formulario.errors)

    def test_guarda_el_email_normalizado_a_minusculas(self):
        formulario = self._formulario(
            self.datos["delegado"], email="Delegado.Nuevo@UIDE.edu.ec")
        self.assertTrue(formulario.is_valid(), formulario.errors.as_text())
        usuario = formulario.save()
        self.assertEqual(usuario.email, "delegado.nuevo@uide.edu.ec")


class SolicitudDeRecuperacionDeContrasena(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_rechaza_un_correo_que_no_existe(self):
        formulario = PasswordResetConValidacionForm(data={"email": "nadie@uide.edu.ec"})
        self.assertFalse(formulario.is_valid())
        self.assertIn("email", formulario.errors)

    def test_rechaza_un_correo_de_cuenta_inactiva(self):
        self.datos["delegado"].is_active = False
        self.datos["delegado"].save()
        formulario = PasswordResetConValidacionForm(data={"email": self.datos["delegado"].email})
        self.assertFalse(formulario.is_valid())

    def test_acepta_el_correo_de_una_cuenta_activa(self):
        formulario = PasswordResetConValidacionForm(data={"email": self.datos["delegado"].email})
        self.assertTrue(formulario.is_valid(), formulario.errors.as_text())
