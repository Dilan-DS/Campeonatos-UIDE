"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

import ast
import importlib
import inspect
import io
import pkgutil
import re
import tempfile
from datetime import date, time, timedelta
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import NoReverseMatch, get_resolver, resolve, reverse
from django.urls.resolvers import URLPattern, URLResolver

from core.forms import ArbitroActaForm, RegistroUsuarioForm
from core.forms.arbitro import ArbitroForm, CrearUsuarioArbitroForm
from core.forms.usuario import (
    CrearUsuarioDelegadoForm, PasswordResetConValidacionForm, PerfilUsuarioForm,
    UsuarioForm,
)
from core.models import (
    Arbitro, Campeonato, Carrera, CodigoQR, Deporte, Equipo,
    EstadisticaJugadorAjedrez, EstadisticaJugadorBasquet,
    EstadisticaJugadorEcuaboly, EstadisticaJugadorFutbol,
    EstadisticaJugadorFutbolin, EstadisticaJugadorPingPong,
    EstadisticaJugadorTenis, EstadisticaJugadorVideojuegos,
    ImagenGaleria, Jugador, Noticia, Pago, Partido, Suspension, Testimonio,
    Transmision, Usuario,
)
from core.utils.calendario import dias_permitidos_de
from core.utils.generar_fixture_eliminatoria import generar_fixture_eliminatoria
from core.utils.generar_fixture_liga import generar_fixture_liga
from core.utils.tabla_posiciones import calcular_tabla_posiciones
from core.validators import normalizar_cedula, validate_ecuadorian_cedula

PWD = "Prueba.2026"

# core/tests/base.py -> parent es core/tests, parent.parent es core/.
RAIZ_PLANTILLAS = Path(__file__).resolve().parent.parent / "templates"


# Las pruebas piden por HTTP. Con DEBUG desactivado (como en CI)
# SECURE_SSL_REDIRECT redirige toda peticion a HTTPS y el cuerpo de la
# respuesta llega vacio, de modo que las comprobaciones fallarian por la
# configuracion y no por el codigo. Se desactiva solo aqui: la
# configuracion real de produccion no se toca.
@override_settings(
    SECURE_SSL_REDIRECT=False,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
    SECURE_HSTS_SECONDS=0,
    # Sin esto, cada test que sube un archivo (logo, comprobante, foto de
    # galeria, QR) lo escribia de verdad en el media/ del proyecto: los
    # FileField no van a la base de datos de pruebas, van al disco. Con
    # MEDIA_ROOT temporal esos archivos quedan aislados y se descartan
    # solos al terminar la corrida.
    MEDIA_ROOT=tempfile.mkdtemp(prefix="uide_test_media_"),
)
class PruebaBase(TestCase):
    """Base comun: las subclases heredan estos ajustes."""


# Rutas del admin de Django y utilidades que no forman parte de esta interfaz.
PREFIJOS_IGNORADOS = (
    "admin", "auth_", "core_", "app_list", "autocomplete", "jsi18n",
    "view_on_site", "password_change", "index", "logout",
)


def _sembrar_archivos_de_media(*rutas_relativas):
    """Crea archivos reales en el MEDIA_ROOT temporal de la corrida actual.

    _datos_base() referencia FileField con una ruta fija ("codigos_qr/qr.png")
    en vez de subir un archivo real: antes colaba porque el media/ real del
    proyecto tenia (por accidente) restos de corridas de test anteriores en
    ese mismo path. Con MEDIA_ROOT aislado (ver PruebaBase) ese atajo
    desaparece, y cualquier validator que llame a FieldFile.size necesita
    que el archivo exista de verdad.
    """
    from django.conf import settings

    raiz = Path(settings.MEDIA_ROOT)
    for relativa in rutas_relativas:
        destino = raiz / relativa
        destino.parent.mkdir(parents=True, exist_ok=True)
        if not destino.exists():
            destino.write_bytes(_imagen_valida().read())


def _datos_base():
    """Conjunto mínimo pero completo para poder resolver cualquier ruta."""
    _sembrar_archivos_de_media(
        "codigos_qr/qr.png", "comprobantes/qr.png", "galeria/x.jpg")
    carrera = Carrera.objects.create(nombre="Ingeniería en TI")
    deporte = Deporte.objects.create(nombre="Fútbol", descripcion="Fútbol 11.")

    def usuario(username, rol, **extra):
        u = Usuario.objects.create_user(
            username=username, email=f"{username}@uide.edu.ec", password=PWD,
            rol=rol, carrera=carrera, genero="masculino", **extra)
        return u

    admin = usuario("admin_test", "ADMIN")
    admin.is_staff = admin.is_superuser = True
    admin.save()
    delegado = usuario("delegado_test", "DELEGADO")
    arb_user = usuario("arbitro_test", "ARBITRO")
    jug_user = usuario("jugador_test", "JUGADOR")

    arbitro = Arbitro.objects.create(
        usuario=arb_user, experiencia="5 años.", contacto="098 000 0000", estado=True)
    arbitro.deportes.add(deporte)

    qr = CodigoQR.objects.create(
        banco="Banco de Loja", numero_cuenta="123456", titular="UIDE Loja",
        tipo_cuenta="AHORROS", activo=True, es_principal=True,
        imagen_qr="codigos_qr/qr.png")

    hoy = date.today()
    campeonato = Campeonato.objects.create(
        nombre="Copa de prueba", tipo_campeonato="LIGA", deporte=deporte,
        descripcion="Campeonato de prueba.", fecha_inicio=hoy - timedelta(days=10),
        fecha_fin=hoy + timedelta(days=30), fecha_fin_inscripcion=hoy - timedelta(days=15),
        estado="EN_CURSO", max_jugadores_por_equipo=18, precio_inscripcion=45,
        activo="SI", es_publico="SI", fixture_generado=True, codigo_qr=qr)

    local = Equipo.objects.create(nombre="Equipo A", campeonato=campeonato,
                                  carrera=carrera, delegado=delegado, aprobado=True)
    visita = Equipo.objects.create(nombre="Equipo B", campeonato=campeonato,
                                   carrera=carrera, delegado=delegado, aprobado=True)

    jugador = Jugador.objects.create(usuario=jug_user, equipo=local,
                                     numero_camiseta=10, posicion="Delantero", edad=21)

    partido = Partido.objects.create(
        campeonato=campeonato, equipo_local=local, equipo_visitante=visita,
        fecha=hoy + timedelta(days=3), hora=time(10, 0), lugar="Cancha 1",
        estado="PROGRAMADO", arbitro=arbitro)

    Pago.objects.create(equipo=local, metodo="TRANSFERENCIA", estado="PENDIENTE",
                        codigo_qr=qr, comprobante_pago="comprobantes/qr.png")
    Suspension.objects.create(jugador=jugador, fecha_inicio=hoy,
                              fecha_fin=hoy + timedelta(days=7), motivo="Roja directa.")
    Noticia.objects.create(titulo="Noticia de prueba", contenido="Contenido.")
    Testimonio.objects.create(autor="Autor de prueba", contenido="Testimonio.")
    ImagenGaleria.objects.create(titulo="Imagen", imagen="galeria/x.jpg")

    return {
        "carrera": carrera, "deporte": deporte, "admin": admin,
        "delegado": delegado, "arbitro": arbitro, "jugador": jugador,
        "campeonato": campeonato, "equipo": local, "partido": partido,
    }


def _rutas():
    """Toda ruta con nombre de la aplicación, resuelta con pks existentes."""
    modelos = {
        "campeonato": Campeonato, "equipo": Equipo, "partido": Partido,
        "jugador": Jugador, "pago": Pago, "deporte": Deporte, "noticia": Noticia,
        "testimonio": Testimonio, "carrera": Carrera, "arbitro": Arbitro,
        "codigo_qr": CodigoQR, "codigos_qr": CodigoQR, "usuario": Usuario,
        "galeria": ImagenGaleria, "imagen_galeria": ImagenGaleria,
        "suspension": Suspension,
    }

    def pk(model):
        obj = model.objects.first()
        return obj.pk if obj else 1

    explicitos = {
        "campeonato_id": pk(Campeonato), "equipo_id": pk(Equipo),
        "jugador_id": pk(Jugador), "partido_id": pk(Partido),
        "usuario_id": pk(Usuario), "suspension_id": pk(Suspension),
        "jugador_usuario_id": pk(Usuario), "uidb64": "MQ", "token": "set-password",
    }

    nombres = []

    def recorrer(patrones):
        for p in patrones:
            if isinstance(p, URLResolver):
                recorrer(p.url_patterns)
            elif isinstance(p, URLPattern) and p.name:
                nombres.append((p.name, tuple(p.pattern.regex.groupindex)))

    recorrer(get_resolver().url_patterns)

    rutas = []
    for nombre, params in sorted(set(nombres)):
        if nombre.startswith(PREFIJOS_IGNORADOS):
            continue
        kwargs = {}
        for prm in params:
            valor = explicitos.get(prm)
            if valor is None:
                valor = next((pk(m) for clave, m in modelos.items() if clave in nombre), 1)
            kwargs[prm] = valor
        try:
            rutas.append((nombre, reverse(nombre, kwargs=kwargs) if kwargs else reverse(nombre)))
        except NoReverseMatch:
            continue
    return sorted(set(rutas))


def _campeonato_vacio(nombre, deporte):
    """Campeonato aparte, sin equipos ni partidos previos.

    Las pruebas de la tabla necesitan controlar todas las filas: si
    reutilizaran el campeonato de _datos_base, sus dos equipos aprobados
    apareceran con ceros y desordenan las comprobaciones.
    """
    hoy = date.today()
    return Campeonato.objects.create(
        nombre=nombre, tipo_campeonato="LIGA", deporte=deporte,
        descripcion="Campeonato para pruebas de calculo.",
        fecha_inicio=hoy - timedelta(days=10), fecha_fin=hoy + timedelta(days=30),
        fecha_fin_inscripcion=hoy - timedelta(days=15), estado="EN_CURSO",
        max_jugadores_por_equipo=18, precio_inscripcion=45,
        activo="SI", es_publico="SI", fixture_generado=True,
        codigo_qr=CodigoQR.objects.first())


def _plantillas_de_pagina():
    """Plantillas que son una pagina completa (extienden comun/base.html).

    Se excluyen los parciales incluidos con {% include %} y los correos,
    que no heredan de la base.
    """
    for ruta in sorted(RAIZ_PLANTILLAS.rglob("*.html")):
        texto = ruta.read_text(encoding="utf-8")
        if "extends 'comun/base.html'" in texto or 'extends "comun/base.html"' in texto:
            yield ruta, texto


def _campeonato_para_calendario(nombre, deporte, dias, tipo="LIGA", duracion=120):
    hoy = date.today()
    return Campeonato.objects.create(
        nombre=nombre, tipo_campeonato=tipo, deporte=deporte,
        descripcion="Campeonato de prueba del calendario.",
        fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=duracion),
        fecha_fin_inscripcion=hoy, estado="INSCRIPCION",
        max_jugadores_por_equipo=11, precio_inscripcion=0,
        activo="SI", es_publico="SI", dias_partido=dias)


def _equipos_para_calendario(campeonato, carrera, delegado, cuantos,
                             genero="masculino", sufijo=""):
    # El nombre es unico por campeonato, asi que se numera y se admite un
    # sufijo para poder anadir equipos a un campeonato que ya tiene otros.
    return [
        Equipo.objects.create(
            nombre=f"{campeonato.pk}-{genero[:3]}-{i}{sufijo}", campeonato=campeonato,
            carrera=carrera, delegado=delegado, aprobado=True, genero=genero)
        for i in range(cuantos)
    ]


def _imagen_valida(nombre="imagen.png"):
    """Un PNG minimo pero real: ImageField lo valida con Pillow, y bytes
    de cabecera PNG escritos a mano no bastan (Pillow los rechaza)."""
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), color=(10, 20, 30)).save(buffer, format="PNG")
    return SimpleUploadedFile(nombre, buffer.getvalue(), content_type="image/png")


def _cerrar(partido, goles_local, goles_visitante):
    """Cierra un partido con marcador, como hace el acta del arbitro."""
    partido.resultado_local = goles_local
    partido.resultado_visitante = goles_visitante
    partido.estado = "FINALIZADO"
    partido.save()
    return partido


def _modulos_de_vistas():
    import core.views as paquete
    for info in pkgutil.iter_modules(paquete.__path__):
        yield info.name, importlib.import_module(f"core.views.{info.name}")


def _definidos_en(modulo):
    """Funciones y clases que define el modulo, no las que importa."""
    return {
        nombre for nombre, objeto in vars(modulo).items()
        if not nombre.startswith("_")
        and getattr(objeto, "__module__", None) == modulo.__name__
        and (inspect.isfunction(objeto) or inspect.isclass(objeto))
    }


__all__ = [
    "ast",
    "importlib",
    "inspect",
    "pkgutil",
    "re",
    "date",
    "time",
    "timedelta",
    "Path",
    "ValidationError",
    "TestCase",
    "override_settings",
    "NoReverseMatch",
    "get_resolver",
    "resolve",
    "reverse",
    "URLPattern",
    "URLResolver",
    "ArbitroActaForm",
    "RegistroUsuarioForm",
    "ArbitroForm",
    "CrearUsuarioArbitroForm",
    "CrearUsuarioDelegadoForm",
    "PasswordResetConValidacionForm",
    "PerfilUsuarioForm",
    "UsuarioForm",
    "Arbitro",
    "Campeonato",
    "Carrera",
    "CodigoQR",
    "Deporte",
    "Equipo",
    "EstadisticaJugadorAjedrez",
    "EstadisticaJugadorBasquet",
    "EstadisticaJugadorEcuaboly",
    "EstadisticaJugadorFutbol",
    "EstadisticaJugadorFutbolin",
    "EstadisticaJugadorPingPong",
    "EstadisticaJugadorTenis",
    "EstadisticaJugadorVideojuegos",
    "ImagenGaleria",
    "Jugador",
    "Noticia",
    "Pago",
    "Partido",
    "Suspension",
    "Testimonio",
    "Transmision",
    "Usuario",
    "dias_permitidos_de",
    "generar_fixture_eliminatoria",
    "generar_fixture_liga",
    "calcular_tabla_posiciones",
    "normalizar_cedula",
    "validate_ecuadorian_cedula",
    "PWD",
    "RAIZ_PLANTILLAS",
    "PruebaBase",
    "PREFIJOS_IGNORADOS",
    "_datos_base",
    "_rutas",
    "_campeonato_vacio",
    "_plantillas_de_pagina",
    "_campeonato_para_calendario",
    "_equipos_para_calendario",
    "_imagen_valida",
    "_cerrar",
    "_modulos_de_vistas",
    "_definidos_en",
]
