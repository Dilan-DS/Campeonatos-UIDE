from django.core.exceptions import ValidationError
from pathlib import Path
import re


MAX_UPLOAD_SIZE = 5 * 1024 * 1024

# Las cedulas ecuatorianas empiezan por el codigo de la provincia de
# emision, del 01 al 24. No se admite el 30 (inscripciones consulares en el
# exterior) porque este sistema es para estudiantes matriculados en Loja; si
# alguna vez hiciera falta, se anade aqui y no en cada formulario.
CODIGOS_DE_PROVINCIA = {f"{numero:02d}" for numero in range(1, 25)}

# Coeficientes del algoritmo Modulo 10, aplicados a los nueve primeros
# digitos. El decimo no entra en la suma: es el digito verificador contra el
# que se compara el resultado.
COEFICIENTES_MODULO_10 = (2, 1, 2, 1, 2, 1, 2, 1, 2)

# Tercer digito: hasta 5 para personas naturales. Del 6 al 9 corresponde a
# otros tipos de identificacion (sociedades, entidades publicas), que no son
# cedulas de ciudadania.
MAXIMO_TERCER_DIGITO = 5


def normalizar_cedula(valor):
    """Limpia el valor antes de guardarlo: espacios fuera, vacio -> None.

    El campo del modelo es unique y admite nulos. Sin esta normalizacion se
    guardaba la cadena vacia, y como "" es igual a "" para el indice unico,
    el segundo usuario sin cedula era rechazado con "Ya existe Usuario con
    este Cedula". Comprobado con dos altas de arbitro sin cedula.
    """
    if valor is None:
        return None
    limpio = str(valor).strip()
    return limpio or None


def validate_ecuadorian_cedula(value):
    """Valida una cedula ecuatoriana con el algoritmo oficial Modulo 10.

    No se limita a comprobar la longitud ni a un patron: calcula el digito
    verificador a partir de los nueve primeros digitos y lo compara con el
    decimo, de modo que un numero inventado de diez cifras se rechaza aunque
    tenga el formato correcto.

    El algoritmo, paso a paso:

      1. Se multiplica cada uno de los nueve primeros digitos por su
         coeficiente (2, 1, 2, 1, 2, 1, 2, 1, 2).
      2. Si un producto pasa de 9 se le restan 9, que equivale a sumar sus
         dos cifras (por ejemplo 8 x 2 = 16 -> 1 + 6 = 7 = 16 - 9).
      3. Se suman los nueve resultados.
      4. El digito verificador es la decena superior menos la suma, es decir
         (10 - suma % 10) % 10. El modulo final cubre el caso en que la suma
         ya sea multiplo de 10, donde el verificador es 0 y no 10.
      5. Ese valor debe coincidir con el decimo digito.

    Se comprueba ademas que la provincia este entre el 01 y el 24 y que el
    tercer digito no pase de 5.

    Lanza ValidationError, que es el mecanismo que ya usan los formularios y
    los campos de modelo del proyecto. Devuelve el valor si es correcto.
    """
    # isinstance cubre None y cualquier tipo que no sea texto; la expresion
    # regular descarta letras, espacios, guiones y cualquier otro caracter,
    # asi como longitudes distintas de 10.
    if not isinstance(value, str) or not re.fullmatch(r"\d{10}", value):
        raise ValidationError("La cédula debe contener exactamente 10 dígitos.")

    if value[:2] not in CODIGOS_DE_PROVINCIA:
        raise ValidationError("La provincia de la cédula no es válida.")

    if int(value[2]) > MAXIMO_TERCER_DIGITO:
        raise ValidationError("El tercer dígito de la cédula no es válido.")

    total = 0
    for digito, coeficiente in zip(map(int, value[:9]), COEFICIENTES_MODULO_10):
        producto = digito * coeficiente
        total += producto - 9 if producto > 9 else producto

    digito_verificador = (10 - total % 10) % 10
    if digito_verificador != int(value[9]):
        raise ValidationError("El dígito verificador de la cédula no es válido.")

    return value


def validate_upload_size(upload):
    """Keep user-controlled uploads bounded before they reach storage."""
    if upload and upload.size > MAX_UPLOAD_SIZE:
        raise ValidationError("El archivo no puede superar 5 MB.")


def validate_pdf_upload(upload):
    validate_upload_size(upload)
    if upload and Path(upload.name).suffix.lower() != ".pdf":
        raise ValidationError("El reglamento debe estar en formato PDF.")
