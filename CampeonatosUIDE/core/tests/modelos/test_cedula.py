"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


class ValidacionCedulaEcuatoriana(TestCase):
    """Algoritmo Modulo 10 de la cedula ecuatoriana.

    IMPORTANTE: todos los numeros de estas pruebas son SINTETICOS. Se
    construyen para que cumplan (o incumplan) el algoritmo; no corresponden
    a ninguna persona real y no se ha comprobado que esten emitidos.
    """

    # Ancla calculada a mano, para que la prueba no dependa de la propia
    # implementacion. Cedula 110544417_ con coeficientes 2,1,2,1,2,1,2,1,2:
    #   1x2=2  1x1=1  0x2=0  5x1=5  4x2=8  4x1=4  4x2=8  1x1=1  7x2=14->5
    #   suma = 2+1+0+5+8+4+8+1+5 = 34
    #   verificador = (10 - 34 % 10) % 10 = 6
    CEDULA_VALIDA = "1105444176"

    @staticmethod
    def cedula_sintetica(prefijo):
        """Completa un prefijo de 9 digitos con su verificador."""
        total = 0
        for indice, caracter in enumerate(prefijo):
            producto = int(caracter) * (2 if indice % 2 == 0 else 1)
            total += producto - 9 if producto > 9 else producto
        return prefijo + str((10 - total % 10) % 10)

    def assert_invalida(self, valor):
        with self.assertRaises(ValidationError):
            validate_ecuadorian_cedula(valor)

    # --- casos que deben pasar -------------------------------------------

    def test_acepta_la_cedula_ancla_calculada_a_mano(self):
        self.assertEqual(validate_ecuadorian_cedula(self.CEDULA_VALIDA), "1105444176")

    def test_el_generador_coincide_con_el_ancla(self):
        self.assertEqual(self.cedula_sintetica("110544417"), self.CEDULA_VALIDA)

    def test_acepta_otras_provincias_validas(self):
        """Una cedula valida se acepta aunque no exista en la base de datos."""
        for provincia in ("01", "09", "17", "24"):
            valor = self.cedula_sintetica(provincia + "3456789"[:7])
            with self.subTest(provincia=provincia):
                self.assertEqual(validate_ecuadorian_cedula(valor), valor)

    def test_acepta_verificador_cero(self):
        """Cuando la suma es multiplo de 10 el verificador es 0, no 10.

        El prefijo 010000009 suma exactamente 10, asi que (10 - 10 % 10) % 10
        da 0. Sin el modulo final saldria 10, que no es un digito.
        """
        valor = self.cedula_sintetica("010000009")
        self.assertEqual(valor, "0100000090")
        self.assertEqual(validate_ecuadorian_cedula(valor), valor)

    # --- casos que deben fallar ------------------------------------------

    def test_rechaza_digito_verificador_modificado(self):
        alterada = self.CEDULA_VALIDA[:-1] + "7"
        self.assert_invalida(alterada)

    def test_rechaza_cualquier_otro_verificador(self):
        """Solo un digito de los diez posibles puede cerrar la cedula."""
        aceptados = []
        for ultimo in "0123456789":
            candidata = self.CEDULA_VALIDA[:-1] + ultimo
            try:
                validate_ecuadorian_cedula(candidata)
                aceptados.append(candidata)
            except ValidationError:
                pass
        self.assertEqual(aceptados, [self.CEDULA_VALIDA])

    def test_rechaza_digito_intermedio_modificado(self):
        self.assert_invalida("1105444276")

    def test_rechaza_diez_digitos_que_no_cumplen_el_algoritmo(self):
        self.assert_invalida("1234567890")

    def test_rechaza_menos_de_diez_digitos(self):
        self.assert_invalida("110544417")

    def test_rechaza_mas_de_diez_digitos(self):
        self.assert_invalida("11054441766")

    def test_rechaza_letras(self):
        for valor in ("11054441A6", "abcdefghij", "110544417X"):
            with self.subTest(valor=valor):
                self.assert_invalida(valor)

    def test_rechaza_caracteres_especiales_y_espacios(self):
        for valor in ("110544417-", "1105-44417", "110 544 417", " 110544417",
                      "1105444176 ", "110544417.", "1105444+76"):
            with self.subTest(valor=valor):
                self.assert_invalida(valor)

    def test_rechaza_cadena_vacia_y_none(self):
        for valor in ("", "   ", None):
            with self.subTest(valor=valor):
                self.assert_invalida(valor)

    def test_rechaza_tipos_que_no_son_texto(self):
        """El validador recibe siempre texto; un entero no debe colarse."""
        for valor in (1105444176, 1.5, [], {}):
            with self.subTest(valor=valor):
                self.assert_invalida(valor)

    def test_rechaza_provincia_fuera_de_rango(self):
        for prefijo in ("00", "25", "30", "99"):
            valor = self.cedula_sintetica(prefijo + "3456789"[:7])
            with self.subTest(prefijo=prefijo):
                self.assert_invalida(valor)

    def test_rechaza_tercer_digito_mayor_que_cinco(self):
        for tercero in "6789":
            valor = self.cedula_sintetica("11" + tercero + "544417"[:6])
            with self.subTest(tercero=tercero):
                self.assert_invalida(valor)


class NormalizacionDeCedula(TestCase):
    """La cedula vacia se guarda como NULL, no como cadena vacia.

    El campo es unique y admite nulos: al guardar "" el segundo usuario sin
    cedula chocaba con el indice unico y el formulario respondia "Ya existe
    Usuario con este Cedula". Comprobado con dos altas de arbitro.
    """

    def test_normaliza_vacios_a_none(self):
        for valor in ("", "   ", None):
            with self.subTest(valor=valor):
                self.assertIsNone(normalizar_cedula(valor))

    def test_recorta_espacios_alrededor(self):
        self.assertEqual(normalizar_cedula("  1105444176  "), "1105444176")

    def test_no_toca_una_cedula_ya_limpia(self):
        self.assertEqual(normalizar_cedula("1105444176"), "1105444176")

