"""Pruebas de regresión de la auditoría de UI/UX.

Cada prueba fija un fallo concreto que se encontró en el proyecto, para que
no vuelva a colarse. La primera clase es un barrido: recorre todas las
rutas con nombre en cada rol y falla si alguna responde 5xx, que es como
se detectaron once vistas rotas.
"""
import ast
import importlib
import inspect
import pkgutil
import re
from datetime import date, time, timedelta
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import NoReverseMatch, get_resolver, resolve, reverse
from django.urls.resolvers import URLPattern, URLResolver

from core.forms import ArbitroActaForm, RegistroUsuarioForm
from core.forms.arbitro import ArbitroForm
from core.forms.usuario import PerfilUsuarioForm, UsuarioForm
from core.models import (
    Arbitro, Campeonato, Carrera, CodigoQR, Deporte, Equipo, ImagenGaleria,
    Jugador, Noticia, Pago, Partido, Suspension, Testimonio, Usuario,
)
from core.utils.tabla_posiciones import calcular_tabla_posiciones
from core.utils.calendario import dias_permitidos_de
from core.utils.generar_fixture_liga import generar_fixture_liga
from core.utils.generar_fixture_eliminatoria import generar_fixture_eliminatoria
from core.validators import normalizar_cedula, validate_ecuadorian_cedula
from django.core.exceptions import ValidationError

PWD = "Prueba.2026"


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
)
class PruebaBase(TestCase):
    """Base comun: las subclases heredan estos ajustes."""


# Rutas del admin de Django y utilidades que no forman parte de esta interfaz.
PREFIJOS_IGNORADOS = (
    "admin", "auth_", "core_", "app_list", "autocomplete", "jsi18n",
    "view_on_site", "password_change", "index", "logout",
)


def _datos_base():
    """Conjunto mínimo pero completo para poder resolver cualquier ruta."""
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


class TodasLasRutasResponden(PruebaBase):
    """Ninguna ruta debe responder 5xx en ningún rol.

    Así se encontraron once vistas rotas: renombres de campo sin actualizar
    la consulta, modelos usados sin importar, plantillas inexistentes y
    formularios que ya no cumplían el contrato de su vista.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _recorrer(self, username=None):
        if username:
            self.assertTrue(self.client.login(username=username, password=PWD),
                            f"no se pudo autenticar {username}")
        fallos = []
        for nombre, url in _rutas():
            try:
                respuesta = self.client.get(url)
            except Exception as exc:                      # noqa: BLE001
                fallos.append(f"{nombre} ({url}): {type(exc).__name__}: {exc}")
                continue
            if respuesta.status_code >= 500:
                fallos.append(f"{nombre} ({url}): HTTP {respuesta.status_code}")
        self.assertEqual(fallos, [], "rutas con error de servidor:\n" + "\n".join(fallos))

    def test_anonimo(self):
        self._recorrer()

    def test_admin(self):
        self._recorrer("admin_test")

    def test_delegado(self):
        self._recorrer("delegado_test")

    def test_arbitro(self):
        self._recorrer("arbitro_test")

    def test_jugador(self):
        self._recorrer("jugador_test")


class CamposRenombradosPorMigracion0003(PruebaBase):
    """Las vistas deben ordenar por los nombres nuevos, no por los antiguos.

    galeria, noticias y testimonios ordenaban por 'fecha' y
    'fecha_publicacion' después de que la migración 0003 los renombrara a
    'creado_en', y las tres respondían FieldError.
    """

    @classmethod
    def setUpTestData(cls):
        _datos_base()

    def test_listados_de_contenido_responden(self):
        for nombre in ("listar_imagenes_galeria", "listar_noticias", "listar_testimonios"):
            with self.subTest(ruta=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)


class VisibilidadPublicaDeCampeonatos(PruebaBase):
    """es_publico es 'SI'/'NO': no puede evaluarse como booleano.

    La plantilla filtraba con `{% if campeonato.es_publico %}`, cierto
    también para 'NO', y publicaba campeonatos marcados como no públicos.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.privado = Campeonato.objects.create(
            nombre="Campeonato privado", tipo_campeonato="LIGA",
            deporte=cls.datos["deporte"], descripcion="No debe publicarse.",
            fecha_inicio=date.today(), fecha_fin=date.today() + timedelta(days=5),
            estado="EN_CURSO", activo="SI", es_publico="NO")

    def test_no_publico_no_aparece(self):
        html = self.client.get(reverse("campeonatos_publicos")).content.decode()
        self.assertIn("Copa de prueba", html)
        self.assertNotIn("Campeonato privado", html)

    def test_portada_solo_publica_los_publicos(self):
        html = self.client.get(reverse("inicio_publico")).content.decode()
        self.assertNotIn("Campeonato privado", html)


class PortadaMuestraDatos(PruebaBase):
    """La portada se renderizaba sin contexto y mostraba siempre sus estados
    vacíos, aunque hubiera campeonatos, partidos y noticias."""

    @classmethod
    def setUpTestData(cls):
        _datos_base()

    def test_portada_incluye_datos_reales(self):
        respuesta = self.client.get(reverse("inicio_publico"))
        self.assertEqual(respuesta.status_code, 200)
        for clave in ("campeonatos", "proximos_partidos", "noticias", "testimonios"):
            self.assertIn(clave, respuesta.context, f"falta {clave} en el contexto")
        self.assertContains(respuesta, "Copa de prueba")
        self.assertNotContains(respuesta, "No hay campeonatos activos")


class PanelAdminMuestraMetricas(PruebaBase):
    """El panel se renderizaba sin contexto y las cuatro métricas salían
    como un guion."""

    @classmethod
    def setUpTestData(cls):
        _datos_base()

    def test_metricas_con_valores(self):
        self.client.login(username="admin_test", password=PWD)
        respuesta = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(respuesta.status_code, 200)
        for clave in ("kpi_usuarios", "kpi_campeonatos", "kpi_equipos", "kpi_arbitros"):
            self.assertIsInstance(respuesta.context[clave], int)
        self.assertEqual(respuesta.context["kpi_equipos"], Equipo.objects.count())


class ContratoDelActaDelArbitro(PruebaBase):
    """ArbitroActaForm perdió su __init__ al migrar los formularios y la
    carga del acta respondía TypeError: ninguna acta podía registrarse."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_el_formulario_acepta_los_jugadores(self):
        jugadores = Jugador.objects.filter(equipo=self.datos["equipo"])
        form = ArbitroActaForm(jugadores_local=jugadores, jugadores_visitante=[])
        for j in jugadores:
            for prefijo in ("goles", "amarillas", "roja", "susp", "susp_ini",
                            "susp_fin", "susp_mot"):
                self.assertIn(f"{prefijo}_{j.id}", form.fields)
        for campo in ("resultado_local", "resultado_visitante", "observaciones",
                      "tarjetas_amarillas_local", "tarjetas_rojas_visitante"):
            self.assertIn(campo, form.fields)

    def test_el_acta_carga_y_guarda(self):
        partido = self.datos["partido"]
        self.client.login(username="arbitro_test", password=PWD)
        url = reverse("acta_partido_arbitro", kwargs={"pk": partido.pk})
        self.assertEqual(self.client.get(url).status_code, 200)

        jugador = Jugador.objects.filter(equipo=partido.equipo_local).first()
        datos = {"resultado_local": 1, "resultado_visitante": 0,
                 "tarjetas_amarillas_local": 0, "tarjetas_amarillas_visitante": 0,
                 "tarjetas_rojas_local": 0, "tarjetas_rojas_visitante": 0,
                 "observaciones": "Sin incidencias.", f"goles_{jugador.id}": 1}
        self.client.post(url, datos)
        partido.refresh_from_db()
        self.assertEqual(partido.resultado_local, 1)
        self.assertEqual(partido.estado, "FINALIZADO")

    def test_rechaza_goles_que_no_cuadran(self):
        partido = self.datos["partido"]
        self.client.login(username="arbitro_test", password=PWD)
        url = reverse("acta_partido_arbitro", kwargs={"pk": partido.pk})
        self.client.post(url, {"resultado_local": 3, "resultado_visitante": 0,
                               "observaciones": ""})
        partido.refresh_from_db()
        self.assertIsNone(partido.resultado_local)
        self.assertEqual(partido.estado, "PROGRAMADO")


class EstadoDePartidoSeMuestraSegunElModelo(PruebaBase):
    """El calendario mapeaba un valor 'JUGADO' inexistente y enviaba todo lo
    demás a "Suspendido": los partidos finalizados se mostraban suspendidos."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_finalizado_no_se_muestra_como_suspendido(self):
        partido = self.datos["partido"]
        partido.estado = "FINALIZADO"
        partido.save()
        self.client.login(username="admin_test", password=PWD)
        html = self.client.get(reverse("calendario_global")).content.decode()
        self.assertIn("Finalizado", html)
        self.assertNotIn("Suspendido", html)

    def test_los_filtros_ofrecen_los_estados_del_modelo(self):
        self.client.login(username="admin_test", password=PWD)
        respuesta = self.client.get(reverse("calendario_global"))
        valores = [v for v, _ in respuesta.context["estados_partido"]]
        self.assertEqual(valores, [v for v, _ in Partido.ESTADOS])
        self.assertNotIn("JUGADO", valores)


class BorradoDeEquipoExigePost(PruebaBase):
    """eliminar_equipo estaba registrado dos veces con nombres de argumento
    distintos; reverse() elegía la variante que la vista no acepta y el
    botón Eliminar respondía TypeError."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_get_no_borra_y_post_si(self):
        equipo = Equipo.objects.create(
            nombre="Equipo desechable", campeonato=self.datos["campeonato"],
            carrera=self.datos["carrera"], delegado=self.datos["delegado"])
        url = reverse("eliminar_equipo", kwargs={"id": equipo.pk})
        self.client.login(username="admin_test", password=PWD)

        self.client.get(url)
        self.assertTrue(Equipo.objects.filter(pk=equipo.pk).exists(),
                        "un GET no debe borrar el equipo")

        self.client.post(url)
        self.assertFalse(Equipo.objects.filter(pk=equipo.pk).exists(),
                         "un POST debe borrar el equipo")


class RegistroRenderizaTodosSusCampos(PruebaBase):
    """La plantilla de registro agrupa los campos por sección; si se añade
    uno al formulario debe seguir apareciendo."""

    def test_ningun_campo_queda_sin_renderizar(self):
        html = self.client.get(reverse("registro")).content.decode()
        for nombre in RegistroUsuarioForm().fields:
            with self.subTest(campo=nombre):
                self.assertIn(f'name="{nombre}"', html)


class PlantillasSinFugasDeSintaxis(PruebaBase):
    """Un comentario {# #} de varias líneas no es un comentario en Django y
    termina impreso en la página."""

    def test_ninguna_plantilla_deja_escapar_etiquetas(self):
        urls = [reverse(n) for n in ("inicio_publico", "login", "registro",
                                     "campeonatos_publicos", "resultados_publicos",
                                     "equipo_publico")]
        for url in urls:
            with self.subTest(url=url):
                html = self.client.get(url).content.decode()
                self.assertNotIn("{%", html)
                self.assertNotIn("{#", html)


class ExportacionesDeEstadisticas(PruebaBase):
    """Las exportaciones leían un campo 'asistencias' que sólo existe en el
    modelo de básquet y respondían AttributeError."""

    @classmethod
    def setUpTestData(cls):
        _datos_base()

    def test_pdf_y_excel_se_generan(self):
        self.client.login(username="admin_test", password=PWD)
        for nombre in ("exportar_estadisticas_pdf", "exportar_estadisticas_excel"):
            with self.subTest(ruta=nombre):
                respuesta = self.client.get(reverse(nombre))
                self.assertEqual(respuesta.status_code, 200)
                self.assertTrue(respuesta["Content-Disposition"].startswith("attachment"))

class EdicionDePartidoAccesiblePorGet(PruebaBase):
    """El enlace "Editar" del calendario es un GET y debe abrir el modal.

    Habia dos rutas con el mismo patron para editar_partido. La primera,
    EditarPartidoView, solo definia post(), asi que atendia la peticion y
    devolvia 405: el modal no se abria nunca y no se podia editar un partido.
    Se conservo la funcion editar_partido, que atiende GET y POST.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_get_abre_el_formulario(self):
        self.client.login(username="admin_test", password=PWD)
        url = reverse("editar_partido", args=[self.datos["partido"].pk])
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, 200, "un GET no debe devolver 405")
        self.assertIsNotNone(respuesta.context.get("partido_a_editar"))
        self.assertIsNotNone(respuesta.context.get("form"))

    def test_post_guarda_los_cambios(self):
        partido = self.datos["partido"]
        self.client.login(username="admin_test", password=PWD)
        self.client.post(reverse("editar_partido", args=[partido.pk]), {
            "campeonato": partido.campeonato_id,
            "equipo_local": partido.equipo_local_id,
            "equipo_visitante": partido.equipo_visitante_id,
            "fecha": partido.fecha.isoformat(),
            "hora": "16:45",
            "lugar": "Cancha nueva",
            "estado": partido.estado,
        })
        partido.refresh_from_db()
        self.assertEqual(partido.lugar, "Cancha nueva")


class FiltroDeEstadoEnElCalendario(PruebaBase):
    """La vista validaba el filtro contra 'JUGADO' y 'SUSPENDIDO'.

    Partido.estado no define esos valores, asi que filtrar por EN_CURSO o
    FINALIZADO se descartaba en silencio y se devolvian todos los partidos.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        campeonato = cls.datos["campeonato"]
        # Un segundo partido, ya finalizado, para poder distinguir el filtro.
        Partido.objects.create(
            campeonato=campeonato,
            equipo_local=cls.datos["equipo"],
            equipo_visitante=Equipo.objects.exclude(pk=cls.datos["equipo"].pk).first(),
            fecha=date.today() - timedelta(days=1), hora=time(9, 0),
            lugar="Cancha 2", estado="FINALIZADO",
            resultado_local=2, resultado_visitante=1,
        )

    def _filtrar(self, estado):
        self.client.login(username="admin_test", password=PWD)
        url = reverse("calendario_global") + (f"?estado={estado}" if estado else "")
        return list(self.client.get(url).context["partidos"])

    def test_cada_estado_filtra_de_verdad(self):
        todos = self._filtrar(None)
        programados = self._filtrar("PROGRAMADO")
        finalizados = self._filtrar("FINALIZADO")

        self.assertEqual(len(todos), 2)
        self.assertEqual(len(programados), 1)
        self.assertEqual(len(finalizados), 1)
        self.assertLess(len(finalizados), len(todos),
                        "FINALIZADO no puede devolver todos los partidos")
        self.assertTrue(all(p.estado == "FINALIZADO" for p in finalizados))

    def test_un_estado_inexistente_no_filtra(self):
        # 'JUGADO' no existe en el modelo: no debe recortar el listado.
        self.assertEqual(len(self._filtrar("JUGADO")), len(self._filtrar(None)))


class RutasHistoricasSiguenResolviendo(PruebaBase):
    """Al resolver los nombres duplicados se conservaron las rutas antiguas.

    Perdieron el name= para que reverse() no fuera ambiguo, pero las URLs
    siguen funcionando para no romper enlaces ya compartidos.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_los_alias_no_devuelven_404(self):
        self.client.login(username="admin_test", password=PWD)
        equipo = self.datos["equipo"].pk
        for url in (f"/equipo/{equipo}/detalle/", "/equipo/nuevo/", "/delegados/registrar/"):
            with self.subTest(url=url):
                self.assertNotEqual(self.client.get(url).status_code, 404,
                                    f"{url} deberia seguir existiendo")


# ---------------------------------------------------------------------------
# Logica de negocio.
#
# Las clases anteriores son de regresion de rutas y de interfaz: comprueban
# que las paginas responden y que muestran lo que deben. Estas cubren los
# calculos y los permisos, que es donde un fallo no se ve en pantalla pero
# deja mal clasificado un campeonato o expone datos de otro equipo.
# ---------------------------------------------------------------------------


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


class TablaDePosicionesCalculaBien(PruebaBase):
    """Puntos, diferencia de goles y desempate de calcular_tabla_posiciones.

    Es el calculo que decide quien gana el campeonato, asi que se comprueba
    con un escenario de resultado conocido en lugar de solo mirar que la
    pagina responda.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.camp = _campeonato_vacio("Liga de calculo", cls.datos["deporte"])

        def equipo(nombre, aprobado=True):
            return Equipo.objects.create(
                nombre=nombre, campeonato=cls.camp, carrera=cls.datos["carrera"],
                delegado=cls.datos["delegado"], aprobado=aprobado)

        cls.a, cls.b, cls.c = equipo("Alfa"), equipo("Beta"), equipo("Gamma")
        cls.sin_aprobar = equipo("Delta", aprobado=False)

        hoy = date.today()

        def partido(local, visitante, gl, gv, estado, dia, hora_):
            return Partido.objects.create(
                campeonato=cls.camp, equipo_local=local, equipo_visitante=visitante,
                fecha=hoy - timedelta(days=dia), hora=time(hora_, 0),
                lugar="Cancha 1", estado=estado,
                resultado_local=gl, resultado_visitante=gv)

        partido(cls.a, cls.b, 3, 1, "FINALIZADO", 5, 10)        # gana Alfa
        partido(cls.b, cls.c, 2, 2, "FINALIZADO", 4, 11)        # empate
        partido(cls.a, cls.c, 9, 0, "PROGRAMADO", 3, 12)        # no cuenta
        partido(cls.a, cls.c, None, None, "FINALIZADO", 2, 13)  # sin marcador

    def _fila(self, tabla, equipo):
        return next(f for f in tabla if f["equipo"].pk == equipo.pk)

    def test_puntos_y_goles_por_equipo(self):
        tabla = calcular_tabla_posiciones(self.camp)

        alfa = self._fila(tabla, self.a)
        self.assertEqual(
            (alfa["pj"], alfa["pg"], alfa["pe"], alfa["pp"], alfa["puntos"]),
            (1, 1, 0, 0, 3), "una victoria son 3 puntos")
        self.assertEqual((alfa["gf"], alfa["gc"], alfa["gd"]), (3, 1, 2))

        beta = self._fila(tabla, self.b)
        self.assertEqual(
            (beta["pj"], beta["pg"], beta["pe"], beta["pp"], beta["puntos"]),
            (2, 0, 1, 1, 1), "un empate es 1 punto y la derrota ninguno")
        self.assertEqual((beta["gf"], beta["gc"], beta["gd"]), (3, 5, -2))

        gamma = self._fila(tabla, self.c)
        self.assertEqual((gamma["pj"], gamma["puntos"], gamma["gd"]), (1, 1, 0))

    def test_desempata_por_diferencia_de_goles(self):
        """Beta y Gamma tienen 1 punto; Gamma va delante por diferencia."""
        orden = [f["equipo"].nombre for f in calcular_tabla_posiciones(self.camp)]
        self.assertEqual(orden[0], "Alfa", "el lider es quien mas puntos tiene")
        self.assertLess(orden.index("Gamma"), orden.index("Beta"),
                        "con los mismos puntos manda la diferencia de goles")

    def test_ignora_partidos_no_finalizados_y_sin_resultado(self):
        """El 9-0 PROGRAMADO y el FINALIZADO sin marcador no deben sumar."""
        alfa = self._fila(calcular_tabla_posiciones(self.camp), self.a)
        self.assertEqual(alfa["pj"], 1, "solo cuenta el partido finalizado con marcador")
        self.assertEqual(alfa["gf"], 3, "el 9-0 programado no debe sumar goles")

    def test_solo_aparecen_equipos_aprobados(self):
        nombres = [f["equipo"].nombre for f in calcular_tabla_posiciones(self.camp)]
        self.assertNotIn("Delta", nombres, "un equipo sin aprobar no va en la tabla")
        self.assertEqual(len(nombres), 3)

    def test_no_mezcla_campeonatos(self):
        """Los equipos del campeonato de _datos_base no deben colarse."""
        nombres = [f["equipo"].nombre for f in calcular_tabla_posiciones(self.camp)]
        self.assertNotIn("Equipo A", nombres)


class FixtureFiltraSegunElRol(PruebaBase):
    """Cada rol solo debe ver en el fixture los partidos que le tocan.

    El delegado ve los de sus equipos, el jugador los de su equipo y el
    arbitro los que dirige. Es una regla de privacidad: sin ella un
    delegado veria el calendario completo del rival.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.camp = _campeonato_vacio("Liga de roles", cls.datos["deporte"])

        cls.otro_delegado = Usuario.objects.create_user(
            username="delegado_rival", email="delegado_rival@uide.edu.ec",
            password=PWD, rol="DELEGADO", carrera=cls.datos["carrera"],
            genero="masculino")

        def equipo(nombre, delegado):
            return Equipo.objects.create(
                nombre=nombre, campeonato=cls.camp, carrera=cls.datos["carrera"],
                delegado=delegado, aprobado=True)

        cls.mio = equipo("Mi equipo", cls.datos["delegado"])
        cls.rival = equipo("Rival", cls.otro_delegado)
        cls.ajeno_a = equipo("Ajeno A", cls.otro_delegado)
        cls.ajeno_b = equipo("Ajeno B", cls.otro_delegado)

        hoy = date.today()
        # Partido de un equipo del delegado de _datos_base, con su arbitro.
        cls.partido_propio = Partido.objects.create(
            campeonato=cls.camp, equipo_local=cls.mio, equipo_visitante=cls.rival,
            fecha=hoy + timedelta(days=1), hora=time(10, 0), lugar="Cancha 1",
            estado="PROGRAMADO", arbitro=cls.datos["arbitro"])
        # Partido entre dos equipos ajenos y sin arbitro asignado.
        cls.partido_ajeno = Partido.objects.create(
            campeonato=cls.camp, equipo_local=cls.ajeno_a,
            equipo_visitante=cls.ajeno_b, fecha=hoy + timedelta(days=2),
            hora=time(11, 0), lugar="Cancha 2", estado="PROGRAMADO")

        cls.url = reverse("fixture_campeonato_detalle", args=[cls.camp.pk])

    def _partidos_visibles(self, usuario):
        self.client.force_login(usuario)
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        return {p.pk for p in respuesta.context["partidos"]}

    def test_el_admin_ve_todos(self):
        visibles = self._partidos_visibles(self.datos["admin"])
        self.assertEqual(visibles, {self.partido_propio.pk, self.partido_ajeno.pk})

    def test_el_delegado_no_ve_partidos_de_otros_equipos(self):
        visibles = self._partidos_visibles(self.datos["delegado"])
        self.assertIn(self.partido_propio.pk, visibles)
        self.assertNotIn(self.partido_ajeno.pk, visibles,
                         "un delegado no debe ver el calendario de equipos ajenos")

    def test_el_jugador_solo_ve_los_de_su_equipo(self):
        jugador = self.datos["jugador"]
        jugador.equipo = self.mio
        jugador.save()
        visibles = self._partidos_visibles(jugador.usuario)
        self.assertEqual(visibles, {self.partido_propio.pk})

    def test_el_arbitro_solo_ve_los_que_dirige(self):
        visibles = self._partidos_visibles(self.datos["arbitro"].usuario)
        self.assertEqual(visibles, {self.partido_propio.pk},
                         "el partido sin arbitro asignado no es suyo")

    def test_un_genero_invalido_cae_en_masculino(self):
        """El parametro genero llega de la URL y no debe filtrar a lo loco."""
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(self.url, {"genero": "no-existe"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["genero_seleccionado"], "masculino")

    def test_filtra_por_genero(self):
        self.rival.genero = "femenino"
        self.rival.save()
        visibles = self._partidos_visibles(self.datos["admin"])
        self.assertNotIn(self.partido_propio.pk, visibles,
                         "un partido con un equipo femenino no va en el fixture masculino")


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


# ---------------------------------------------------------------------------
# Diseño de la interfaz.
#
# Estas revisan las plantillas como ficheros, no las vistas: son las que
# evitan que vuelvan a colarse clases sin estilo, paginas sin titulo o
# encabezados mal jerarquizados. Todo lo que comprueban aparecio de verdad
# en la auditoria.
# ---------------------------------------------------------------------------

RAIZ_PLANTILLAS = Path(__file__).resolve().parent / "templates"


def _plantillas_de_pagina():
    """Plantillas que son una pagina completa (extienden comun/base.html).

    Se excluyen los parciales incluidos con {% include %} y los correos,
    que no heredan de la base.
    """
    for ruta in sorted(RAIZ_PLANTILLAS.rglob("*.html")):
        texto = ruta.read_text(encoding="utf-8")
        if "extends 'comun/base.html'" in texto or 'extends "comun/base.html"' in texto:
            yield ruta, texto


class PlantillasSinClasesDeBootstrap(PruebaBase):
    """Ninguna clase de Bootstrap ni de Tailwind en las plantillas.

    El proyecto usa Bulma. Habia 248 usos de clases que no existian en
    ninguna de las dos hojas cargadas, asi que las tablas salian sin
    cebreado, las rejillas no rejillaban y los avisos sin recuadro.
    """

    # Solo clases que no existen en Bulma. Ojo con los prefijos: Bulma si
    # tiene has-text-centered, por eso se ancla el token completo.
    PROHIBIDAS = (
        "row", "col-md-6", "col-md-12", "col-sm-6", "offset-md-3",
        "d-flex", "form-select", "form-control", "me-2", "ms-2",
        "table-responsive", "table-striped", "table-hover", "table-bordered",
        "table-dark", "alert-info", "alert-danger", "text-muted", "bg-info",
        "btn-primary", "hero-strip", "section-pad", "max-w-2xl",
        "mt-2-mobile", "is-256x256", "text-center",
    )

    def test_ninguna_clase_de_otro_framework(self):
        encontradas = []
        for ruta in sorted(RAIZ_PLANTILLAS.rglob("*.html")):
            texto = ruta.read_text(encoding="utf-8")
            for valor in re.findall(r'class\s*=\s*"([^"]*)"', texto):
                # quitar las etiquetas de Django antes de partir en tokens
                limpio = re.sub(r"\{[{%].*?[%}]\}", " ", valor)
                for token in limpio.split():
                    if token in self.PROHIBIDAS:
                        encontradas.append(
                            f"{ruta.relative_to(RAIZ_PLANTILLAS).as_posix()}: {token}")
        self.assertEqual(encontradas, [],
                         "clases sin ningun estilo detras:\n" + "\n".join(encontradas))


class CadaPaginaTieneTituloPropio(PruebaBase):
    """Diez paginas caian en el titulo por defecto de base.html.

    Con varias pestanas abiertas no habia forma de distinguirlas, y un
    lector de pantalla anuncia el mismo nombre en todas.
    """

    def test_todas_declaran_block_title(self):
        sin_titulo = [
            ruta.relative_to(RAIZ_PLANTILLAS).as_posix()
            for ruta, texto in _plantillas_de_pagina()
            if "block title" not in texto
        ]
        self.assertEqual(sin_titulo, [],
                         "paginas sin titulo propio: " + ", ".join(sin_titulo))


class CadaPaginaTieneUnEncabezadoPrincipal(PruebaBase):
    """Dieciocho paginas empezaban en <h2> sin ningun <h1>."""

    def test_todas_tienen_h1(self):
        sin_h1 = [
            ruta.relative_to(RAIZ_PLANTILLAS).as_posix()
            for ruta, texto in _plantillas_de_pagina()
            if "<h1" not in texto
        ]
        self.assertEqual(sin_h1, [], "paginas sin <h1>: " + ", ".join(sin_h1))


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


class EstadisticasDeCadaDeporteUsanCamposQueExisten(PruebaBase):
    """Ajedrez y videojuegos pedian stat.partidas_jugadas, inexistente.

    El campo de esos modelos es partidos_jugados, asi que la columna
    "Partidas jugadas" salia siempre vacia.
    """

    def test_los_campos_declarados_existen_en_su_modelo(self):
        from core.views.estadisticas_views import DEPORTES_CON_ESTADISTICA
        for deporte, modelo, columnas in DEPORTES_CON_ESTADISTICA:
            nombres = {f.name for f in modelo._meta.get_fields() if f.concrete}
            for etiqueta, campo in columnas:
                with self.subTest(deporte=deporte, campo=campo):
                    self.assertIn(campo, nombres,
                                  f"{modelo.__name__} no tiene {campo}")

    def test_las_plantillas_por_deporte_no_dejan_celdas_vacias(self):
        from django.template.loader import render_to_string

        class Camp:
            nombre = "Copa de prueba"

        class Us:
            username = "jugador1"

        class Eq:
            nombre = "Titanes TI"

        class Jug:
            usuario = Us()
            equipo = Eq()

        class Stat:
            jugador = Jug()
            campeonato = Camp()
            partidos_jugados = 7
            goles = 3
            tarjetas_amarillas = 1
            tarjetas_rojas = 0
            canastas = 22
            rebotes = 9
            asistencias = 4
            partidas_ganadas = 5
            partidas_empatadas = 1
            partidas_perdidas = 1
            sets_ganados = 6
            sets_perdidos = 2
            partidos_ganados = 4
            partidos_perdidos = 3

        contexto = {"estadisticas": [Stat()], "campeonatos": [],
                    "selected_campeonato_id": None}
        for deporte in ("futbol", "basquet", "ajedrez", "ecuaboly",
                        "pingpong", "tenis", "futbolin", "videojuegos"):
            with self.subTest(deporte=deporte):
                html = render_to_string(
                    f"estadisticas/estadisticas_{deporte}.html", contexto)
                self.assertNotIn("<td></td>", html,
                                 "ninguna columna debe quedar vacia")
                self.assertNotIn("None", html)


# ---------------------------------------------------------------------------
# Control de acceso.
#
# Cada clase fija una vulnerabilidad que se comprobo explotable en la
# auditoria, y comprueba tambien que el uso legitimo sigue funcionando:
# cerrar un agujero sin dejar fuera a quien si tiene derecho.
# ---------------------------------------------------------------------------


class TestimoniosExigenSesion(PruebaBase):
    """Registrar/Editar/EliminarTestimonio eran `View` sin comprobacion.

    Comprobado antes del arreglo: un cliente sin sesion creaba, editaba y
    borraba testimonios.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_un_anonimo_no_puede_crear(self):
        antes = Testimonio.objects.count()
        self.client.post(reverse("registrar_testimonio"),
                         {"autor": "Atacante", "contenido": "Sin sesion."})
        self.assertEqual(Testimonio.objects.count(), antes,
                         "un anonimo no debe poder crear testimonios")

    def test_un_anonimo_no_puede_editar_ni_borrar(self):
        testimonio = Testimonio.objects.first()
        autor = testimonio.autor
        self.client.post(reverse("editar_testimonio", args=[testimonio.id]),
                         {"autor": "Modificado", "contenido": "x"})
        testimonio.refresh_from_db()
        self.assertEqual(testimonio.autor, autor, "no debe poder editarlo")

        self.client.post(reverse("eliminar_testimonio", args=[testimonio.id]))
        self.assertTrue(Testimonio.objects.filter(id=testimonio.id).exists(),
                        "no debe poder borrarlo")

    def test_un_jugador_tampoco(self):
        self.client.force_login(self.datos["jugador"].usuario)
        antes = Testimonio.objects.count()
        self.client.post(reverse("registrar_testimonio"),
                         {"autor": "Jugador", "contenido": "x"})
        self.assertEqual(Testimonio.objects.count(), antes)

    def test_el_admin_si_puede(self):
        """El arreglo no debe dejar fuera a quien si gestiona testimonios."""
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(reverse("registrar_testimonio"))
        self.assertEqual(respuesta.status_code, 200)

    def test_el_listado_sigue_siendo_publico(self):
        self.assertEqual(self.client.get(reverse("listar_testimonios")).status_code, 200)


class SuspensionesNoSonPublicas(PruebaBase):
    """El expediente disciplinario llevaba nombre y motivo, y era publico."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_un_anonimo_no_ve_el_listado(self):
        respuesta = self.client.get(reverse("listar_suspensiones"))
        self.assertEqual(respuesta.status_code, 302,
                         "debe redirigir al login, no responder 200")

    def test_un_anonimo_no_ve_el_detalle(self):
        suspension = Suspension.objects.first()
        respuesta = self.client.get(reverse("detalle_suspension", args=[suspension.id]))
        self.assertEqual(respuesta.status_code, 302)

    def test_el_admin_sigue_viendo_todo(self):
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(reverse("listar_suspensiones"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.context["suspensiones"]), Suspension.objects.count())

    def test_un_jugador_solo_ve_la_suya(self):
        otro = Usuario.objects.create_user(
            username="jugador_sin_sancion", email="jsn@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="masculino")
        Jugador.objects.create(usuario=otro, equipo=self.datos["equipo"],
                               numero_camiseta=11, posicion="Defensa", edad=20)
        self.client.force_login(otro)
        respuesta = self.client.get(reverse("listar_suspensiones"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(list(respuesta.context["suspensiones"]), [],
                         "no debe ver expedientes de otros jugadores")

    def test_pedir_un_expediente_ajeno_da_404(self):
        otro = Usuario.objects.create_user(
            username="jugador_curioso", email="jc@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="masculino")
        Jugador.objects.create(usuario=otro, equipo=self.datos["equipo"],
                               numero_camiseta=12, posicion="Portero", edad=22)
        self.client.force_login(otro)
        suspension = Suspension.objects.first()
        respuesta = self.client.get(reverse("detalle_suspension", args=[suspension.id]))
        self.assertEqual(respuesta.status_code, 404,
                         "404 y no 403: no debe confirmar que el expediente existe")


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


class CatalogoQrSeSerializaEscapado(PruebaBase):
    """El catalogo iba con json.dumps y |safe dentro de un <script>.

    json.dumps no escapa < ni >, asi que un "</script>" en cualquier campo
    del QR (banco, titular, numero de cuenta) cerraba el bloque y el resto
    se interpretaba como HTML: XSS almacenado contra los delegados.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_una_carga_en_el_banco_no_rompe_el_script(self):
        qr = CodigoQR.objects.first()
        qr.banco = '</script><img src=x onerror=alert(1)>'
        qr.save()

        self.client.force_login(self.datos["delegado"])
        respuesta = self.client.get(
            reverse("registrar_pago_equipo", args=[self.datos["equipo"].pk]))
        self.assertEqual(respuesta.status_code, 200)
        cuerpo = respuesta.content.decode()

        self.assertNotIn("</script><img", cuerpo,
                         "la carga no debe salir literal y cerrar el <script>")
        self.assertIn("\\u003C", cuerpo,
                      "json_script debe escapar el < como \\u003C")


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



# ---------------------------------------------------------------------------
# Generacion del calendario.
#
# Cada clase fija un fallo que se reprodujo antes de corregirlo: el comando
# que no arrancaba, el campeonato sin dias que devolvia un error 500, la
# regeneracion fallida que borraba el calendario y los partidos que caian a
# la vez en la misma cancha.
# ---------------------------------------------------------------------------


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


class ElComandoDeCalendarioArranca(PruebaBase):
    """Importaba asignar_arbitros_a_partidos, que no existe en el proyecto.

    El comando aparecia en `manage.py help` pero fallaba con ImportError
    antes de ejecutar nada.
    """

    def test_el_modulo_se_importa(self):
        from core.management.commands import generar_fixtures  # noqa: F401

    def test_el_comando_se_ejecuta_sin_campeonatos_pendientes(self):
        from io import StringIO
        from django.core.management import call_command

        salida = StringIO()
        call_command("generar_fixtures", stdout=salida, stderr=StringIO())
        self.assertIn("No hay campeonatos", salida.getvalue())

    def test_el_comando_genera_el_calendario_de_punta_a_punta(self):
        """Campeonato con la inscripcion cerrada: el comando debe programarlo."""
        from io import StringIO
        from django.core.management import call_command

        datos = _datos_base()
        camp = _campeonato_para_calendario(
            "Comando liga", datos["deporte"], ["LUNES", "MIERCOLES"])
        camp.fecha_fin_inscripcion = date.today() - timedelta(days=1)
        camp.fixture_generado = False
        camp.estado = "INSCRIPCION"
        camp.save()
        _equipos_para_calendario(camp, datos["carrera"], datos["delegado"], 4)

        salida = StringIO()
        call_command("generar_fixtures", stdout=salida, stderr=StringIO())

        camp.refresh_from_db()
        self.assertEqual(Partido.objects.filter(campeonato=camp).count(), 6)
        self.assertTrue(camp.fixture_generado)
        self.assertEqual(camp.estado, "EN_CURSO")
        self.assertIn("finalizado", salida.getvalue())


class CampeonatoSinDiasNoRompe(PruebaBase):
    """dias_partido admite vacio (blank=True, default=[]).

    Con la lista vacia el bucle que buscaba fecha no terminaba: avanzaba
    hasta pasar del ano 9999 y lanzaba OverflowError, que desde la web
    salia como un error 500.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_liga_sin_dias_genera_igualmente(self):
        camp = _campeonato_para_calendario("Liga sin dias", self.datos["deporte"], [])
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4)
        creados = generar_fixture_liga(camp.id)
        self.assertEqual(creados, 6, "4 equipos son 6 partidos, con o sin dias marcados")

    def test_eliminatoria_sin_dias_genera_igualmente(self):
        camp = _campeonato_para_calendario(
            "Elim sin dias", self.datos["deporte"], [], tipo="ELIMINATORIA")
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4)
        self.assertEqual(generar_fixture_eliminatoria(camp.id), 2)

    def test_un_dia_desconocido_no_rompe(self):
        """Si el dato guardado no esta en el mapa, se permiten los siete."""
        self.assertEqual(dias_permitidos_de(_ConDias(["MIÉRCOLES"])), list(range(7)))
        self.assertEqual(dias_permitidos_de(_ConDias([])), list(range(7)))
        self.assertEqual(dias_permitidos_de(_ConDias(["SABADO"])), [5])

    def test_la_vista_no_devuelve_error_500(self):
        camp = _campeonato_para_calendario("Web sin dias", self.datos["deporte"], [])
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4)
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(
            reverse("generar_fixture_campeonato", args=[camp.id]))
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(Partido.objects.filter(campeonato=camp).count(), 6)


class _ConDias:
    """Objeto minimo con dias_partido, para probar el helper sin tocar la BD."""

    def __init__(self, dias):
        self.dias_partido = dias


class RegenerarNoPierdeElCalendario(PruebaBase):
    """La vista borraba los partidos antes de generar y fuera de transaccion.

    Si la generacion fallaba, el campeonato se quedaba sin calendario:
    comprobado, 6 partidos programados pasaban a 0.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _camp_con_calendario(self):
        camp = _campeonato_para_calendario(
            "Regenerar", self.datos["deporte"], ["LUNES", "MIERCOLES"])
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4)
        self.client.force_login(self.datos["admin"])
        self.client.post(reverse("generar_fixture_campeonato", args=[camp.id]))
        return camp

    def test_si_no_se_generan_partidos_se_conserva_el_anterior(self):
        """Dos equipos aprobados pero de generos distintos.

        Asi se supera la guarda de "al menos 2 equipos aprobados" de la
        vista y se llega de verdad al borrado: cada genero se queda con un
        solo equipo, la generacion devuelve 0 y hay que revertir.
        """
        camp = self._camp_con_calendario()
        antes = Partido.objects.filter(campeonato=camp).count()
        self.assertEqual(antes, 6)

        Equipo.objects.filter(campeonato=camp).update(aprobado=False)
        _equipos_para_calendario(camp, self.datos["carrera"],
                                 self.datos["delegado"], 1, "masculino", "-bis")
        _equipos_para_calendario(camp, self.datos["carrera"],
                                 self.datos["delegado"], 1, "femenino", "-bis")
        self.assertEqual(
            Equipo.objects.filter(campeonato=camp, aprobado=True).count(), 2,
            "la vista debe pasar su guarda previa y llegar al borrado")

        respuesta = self.client.post(
            reverse("generar_fixture_campeonato", args=[camp.id]))
        self.assertEqual(respuesta.status_code, 302)

        self.assertEqual(Partido.objects.filter(campeonato=camp).count(), antes,
                         "el calendario anterior no debe perderse")

    def test_regenerar_bien_sustituye_el_calendario(self):
        """El caso normal debe seguir funcionando."""
        camp = self._camp_con_calendario()
        ids_antes = set(Partido.objects.filter(campeonato=camp).values_list("id", flat=True))
        self.client.post(reverse("generar_fixture_campeonato", args=[camp.id]))
        ids_despues = set(Partido.objects.filter(campeonato=camp).values_list("id", flat=True))
        self.assertEqual(len(ids_despues), 6)
        self.assertFalse(ids_antes & ids_despues, "deben ser partidos nuevos")


class NoHayDosPartidosEnLaMismaCanchaYHora(PruebaBase):
    """Toda la jornada se creaba a las 18:00 con Cancha aleatoria 1-5.

    Dos partidos de la misma jornada podian caer a la vez en la misma
    cancha.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_sin_solapes_de_cancha(self):
        for n in (4, 6, 8, 10, 12):
            with self.subTest(equipos=n):
                camp = _campeonato_para_calendario(
                    f"Canchas {n}", self.datos["deporte"], ["LUNES"])
                _equipos_para_calendario(
                    camp, self.datos["carrera"], self.datos["delegado"], n)
                generar_fixture_liga(camp.id)

                ocupacion = [
                    (p.fecha, p.hora, p.lugar)
                    for p in Partido.objects.filter(campeonato=camp)
                ]
                self.assertEqual(len(ocupacion), len(set(ocupacion)),
                                 "dos partidos no pueden compartir fecha, hora y cancha")

    def test_los_primeros_cinco_van_a_las_seis(self):
        """Con cinco canchas libres no hace falta mover la hora."""
        camp = _campeonato_para_calendario(
            "Canchas horario", self.datos["deporte"], ["LUNES"])
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 10)
        generar_fixture_liga(camp.id)
        primera_jornada = Partido.objects.filter(campeonato=camp).order_by("fecha")[:5]
        self.assertTrue(all(p.hora.hour == 18 for p in primera_jornada))
        self.assertEqual(
            sorted(p.lugar for p in primera_jornada),
            ["Cancha 1", "Cancha 2", "Cancha 3", "Cancha 4", "Cancha 5"])


class ElEmparejamientoSigueSiendoCorrecto(PruebaBase):
    """Red de seguridad del algoritmo: los arreglos no deben alterarlo."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_todos_contra_todos(self):
        for n in (2, 3, 4, 5, 6, 8):
            with self.subTest(equipos=n):
                camp = _campeonato_para_calendario(
                    f"Liga check {n}", self.datos["deporte"], ["LUNES", "MIERCOLES", "VIERNES"])
                _equipos_para_calendario(
                    camp, self.datos["carrera"], self.datos["delegado"], n)
                creados = generar_fixture_liga(camp.id)
                self.assertEqual(creados, n * (n - 1) // 2)

                partidos = list(Partido.objects.filter(campeonato=camp))
                parejas = [frozenset((p.equipo_local_id, p.equipo_visitante_id))
                           for p in partidos]
                self.assertEqual(len(parejas), len(set(parejas)))
                for p in partidos:
                    self.assertNotEqual(p.equipo_local_id, p.equipo_visitante_id)

    def test_nadie_juega_dos_veces_el_mismo_dia(self):
        camp = _campeonato_para_calendario(
            "Liga dias check", self.datos["deporte"], ["LUNES", "MIERCOLES"])
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 6)
        generar_fixture_liga(camp.id)
        por_dia = {}
        for p in Partido.objects.filter(campeonato=camp):
            por_dia.setdefault(p.fecha, []).extend(
                [p.equipo_local_id, p.equipo_visitante_id])
        for fecha, equipos in por_dia.items():
            self.assertEqual(len(equipos), len(set(equipos)), f"solape el {fecha}")

    def test_solo_dias_permitidos(self):
        camp = _campeonato_para_calendario(
            "Liga sabados", self.datos["deporte"], ["SABADO"])
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_liga(camp.id)
        for p in Partido.objects.filter(campeonato=camp):
            self.assertEqual(p.fecha.weekday(), 5)

    def test_los_generos_no_se_cruzan(self):
        camp = _campeonato_para_calendario(
            "Liga mixta check", self.datos["deporte"], ["LUNES", "MIERCOLES"])
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4, "masculino")
        _equipos_para_calendario(camp, self.datos["carrera"], self.datos["delegado"], 4, "femenino")
        self.assertEqual(generar_fixture_liga(camp.id), 12)
        for p in Partido.objects.filter(campeonato=camp):
            self.assertEqual(p.equipo_local.genero, p.equipo_visitante.genero)


# ---------------------------------------------------------------------------
# Avance del cuadro de eliminatoria.
#
# generar_fixture_eliminatoria solo creaba la primera ronda: con 8 equipos
# programaba 4 cruces y ahi se quedaba, cuando el cuadro completo necesita
# 7 partidos. Ahora los ganadores cruzan solos al cerrarse la ronda, y hay
# un boton manual de respaldo.
# ---------------------------------------------------------------------------


def _cerrar(partido, goles_local, goles_visitante):
    """Cierra un partido con marcador, como hace el acta del arbitro."""
    partido.resultado_local = goles_local
    partido.resultado_visitante = goles_visitante
    partido.estado = "FINALIZADO"
    partido.save()
    return partido


class CuadroDeEliminatoriaAvanzaSolo(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _cuadro(self, equipos, nombre="Copa"):
        camp = _campeonato_para_calendario(
            nombre, self.datos["deporte"], ["LUNES", "MIERCOLES", "VIERNES"],
            tipo="ELIMINATORIA")
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], equipos)
        generar_fixture_eliminatoria(camp.id)
        return camp

    def _ronda(self, camp, numero):
        return list(Partido.objects.filter(campeonato=camp, ronda=numero)
                    .order_by("fecha", "hora", "id"))

    def test_la_primera_ronda_queda_marcada_como_ronda_1(self):
        camp = self._cuadro(8)
        self.assertEqual(len(self._ronda(camp, 1)), 4)

    def test_ocho_equipos_llegan_hasta_la_final(self):
        """4 cuartos + 2 semifinales + 1 final = 7 partidos."""
        camp = self._cuadro(8)

        for partido in self._ronda(camp, 1):
            _cerrar(partido, 2, 1)          # gana siempre el local
        semifinales = self._ronda(camp, 2)
        self.assertEqual(len(semifinales), 2, "deben crearse 2 semifinales solas")

        for partido in semifinales:
            _cerrar(partido, 3, 0)
        final = self._ronda(camp, 3)
        self.assertEqual(len(final), 1, "debe crearse la final sola")

        _cerrar(final[0], 1, 0)
        self.assertEqual(Partido.objects.filter(campeonato=camp).count(), 7)
        self.assertEqual(self._ronda(camp, 4), [], "despues de la final no hay mas")

    def test_no_avanza_hasta_que_termina_toda_la_ronda(self):
        camp = self._cuadro(8)
        cuartos = self._ronda(camp, 1)
        for partido in cuartos[:3]:
            _cerrar(partido, 1, 0)
        self.assertEqual(self._ronda(camp, 2), [],
                         "con un partido sin jugar no debe cruzarse nada")

        _cerrar(cuartos[3], 1, 0)
        self.assertEqual(len(self._ronda(camp, 2)), 2)

    def test_un_empate_bloquea_el_avance(self):
        """Sin penaltis ni desempate, un empate no puede decidir quien pasa."""
        camp = self._cuadro(4)
        for partido in self._ronda(camp, 1):
            _cerrar(partido, 1, 1)
        self.assertEqual(self._ronda(camp, 2), [],
                         "un empate no debe generar la ronda siguiente")

    def test_corregir_el_empate_desbloquea(self):
        camp = self._cuadro(4)
        primera = self._ronda(camp, 1)
        for partido in primera:
            _cerrar(partido, 1, 1)
        self.assertEqual(self._ronda(camp, 2), [])

        for partido in primera:
            _cerrar(partido, 2, 1)
        self.assertEqual(len(self._ronda(camp, 2)), 1, "ya hay ganadores: se crea la final")

    def test_los_equipos_con_bye_entran_en_la_segunda_ronda(self):
        """Con 5 equipos, 3 descansan en la primera ronda."""
        camp = self._cuadro(5)
        primera = self._ronda(camp, 1)
        self.assertEqual(len(primera), 1, "5 equipos -> 8 plazas -> 1 solo cruce")

        _cerrar(primera[0], 2, 0)
        segunda = self._ronda(camp, 2)
        self.assertEqual(len(segunda), 2, "el ganador y los 3 que descansaron son 4")

        jugaron = {e for p in segunda for e in (p.equipo_local_id, p.equipo_visitante_id)}
        self.assertEqual(len(jugaron), 4)
        self.assertNotIn(primera[0].equipo_visitante_id, jugaron,
                         "el eliminado no puede reaparecer")

    def test_el_perdedor_no_vuelve_a_jugar(self):
        camp = self._cuadro(8)
        perdedores = set()
        for partido in self._ronda(camp, 1):
            _cerrar(partido, 3, 1)
            perdedores.add(partido.equipo_visitante_id)

        for partido in self._ronda(camp, 2):
            self.assertNotIn(partido.equipo_local_id, perdedores)
            self.assertNotIn(partido.equipo_visitante_id, perdedores)

    def test_la_ronda_siguiente_respeta_los_dias_permitidos(self):
        camp = _campeonato_para_calendario(
            "Copa sabados", self.datos["deporte"], ["SABADO"], tipo="ELIMINATORIA")
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_eliminatoria(camp.id)
        for partido in self._ronda(camp, 1):
            _cerrar(partido, 1, 0)
        for partido in self._ronda(camp, 2):
            self.assertEqual(partido.fecha.weekday(), 5)

    def test_la_ronda_siguiente_se_juega_despues(self):
        camp = self._cuadro(4)
        primera = self._ronda(camp, 1)
        for partido in primera:
            _cerrar(partido, 1, 0)
        ultima_de_la_primera = max(p.fecha for p in primera)
        for partido in self._ronda(camp, 2):
            self.assertGreater(partido.fecha, ultima_de_la_primera)

    def test_una_liga_no_se_ve_afectada(self):
        """El avance solo aplica a ELIMINATORIA."""
        camp = _campeonato_para_calendario(
            "Liga intacta", self.datos["deporte"], ["LUNES", "MIERCOLES"])
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_liga(camp.id)
        antes = Partido.objects.filter(campeonato=camp).count()
        for partido in Partido.objects.filter(campeonato=camp):
            _cerrar(partido, 2, 1)
        self.assertEqual(Partido.objects.filter(campeonato=camp).count(), antes,
                         "una liga no debe generar rondas nuevas")


class BotonManualDeAvance(PruebaBase):
    """Respaldo por si el avance automatico no se hubiera disparado."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _cuadro_con_ronda_cerrada(self):
        camp = _campeonato_para_calendario(
            "Copa boton", self.datos["deporte"], ["LUNES", "MIERCOLES"],
            tipo="ELIMINATORIA")
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_eliminatoria(camp.id)
        return camp

    def test_el_boton_crea_la_ronda_si_falta(self):
        camp = self._cuadro_con_ronda_cerrada()
        # Se cierran los partidos sin pasar por el save() del modelo, de modo
        # que la senal no salta: simula el caso que el boton debe cubrir.
        for partido in Partido.objects.filter(campeonato=camp, ronda=1):
            Partido.objects.filter(pk=partido.pk).update(
                resultado_local=2, resultado_visitante=0, estado="FINALIZADO")
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 0)

        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(
            reverse("avanzar_ronda_eliminatoria", args=[camp.id]))
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 1)

    def test_pulsarlo_dos_veces_no_duplica(self):
        camp = self._cuadro_con_ronda_cerrada()
        for partido in Partido.objects.filter(campeonato=camp, ronda=1):
            _cerrar(partido, 2, 0)
        self.client.force_login(self.datos["admin"])
        url = reverse("avanzar_ronda_eliminatoria", args=[camp.id])
        self.client.post(url)
        self.client.post(url)
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 1,
                         "no debe crear la misma ronda dos veces")

    def test_un_jugador_no_puede_usarlo(self):
        camp = self._cuadro_con_ronda_cerrada()
        self.client.force_login(self.datos["jugador"].usuario)
        respuesta = self.client.post(
            reverse("avanzar_ronda_eliminatoria", args=[camp.id]))
        self.assertIn(respuesta.status_code, (302, 403))
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 0)

    def test_avisa_cuando_hay_un_empate(self):
        camp = self._cuadro_con_ronda_cerrada()
        for partido in Partido.objects.filter(campeonato=camp, ronda=1):
            Partido.objects.filter(pk=partido.pk).update(
                resultado_local=1, resultado_visitante=1, estado="FINALIZADO")
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(
            reverse("avanzar_ronda_eliminatoria", args=[camp.id]), follow=True)
        textos = [m.message for m in respuesta.context["messages"]]
        self.assertTrue(any("empatado" in t for t in textos),
                        f"deberia explicar el empate: {textos}")

    def test_avisa_cuando_la_ronda_sigue_en_juego(self):
        camp = self._cuadro_con_ronda_cerrada()
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(
            reverse("avanzar_ronda_eliminatoria", args=[camp.id]), follow=True)
        textos = [m.message for m in respuesta.context["messages"]]
        self.assertTrue(any("sin jugar" in t for t in textos),
                        f"deberia decir que faltan partidos: {textos}")

    def test_el_boton_aparece_solo_en_eliminatoria(self):
        camp = self._cuadro_con_ronda_cerrada()
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(
            reverse("fixture_campeonato_detalle", args=[camp.id]))
        self.assertTrue(respuesta.context["puede_avanzar_ronda"])

        liga = _campeonato_para_calendario(
            "Liga sin boton", self.datos["deporte"], ["LUNES"])
        _equipos_para_calendario(
            liga, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_liga(liga.id)
        respuesta = self.client.get(
            reverse("fixture_campeonato_detalle", args=[liga.id]))
        self.assertFalse(respuesta.context["puede_avanzar_ronda"])


# ---------------------------------------------------------------------------
# Tanda de penaltis.
#
# Un empate no puede decidir quien pasa de ronda. La tanda es lo unico que
# lo resuelve, y no cuenta como goles: no debe tocar la tabla de posiciones.
# ---------------------------------------------------------------------------


class ReglasDeLaTandaDePenales(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _partido(self, gl, gv, pl=None, pv=None):
        camp = self.datos["campeonato"]
        return Partido(
            campeonato=camp,
            equipo_local=self.datos["equipo"],
            equipo_visitante=Equipo.objects.filter(campeonato=camp)
                                           .exclude(pk=self.datos["equipo"].pk).first(),
            fecha=date.today(), hora=time(18, 0), lugar="Cancha 1",
            resultado_local=gl, resultado_visitante=gv,
            penales_local=pl, penales_visitante=pv)

    def test_sin_tanda_es_valido(self):
        self._partido(2, 1).clean()
        self._partido(1, 1).clean()

    def test_la_tanda_exige_los_dos_equipos(self):
        with self.assertRaises(ValidationError) as caso:
            self._partido(1, 1, pl=4).clean()
        self.assertIn("los dos equipos", caso.exception.messages[0])

        with self.assertRaises(ValidationError):
            self._partido(1, 1, pv=4).clean()

    def test_la_tanda_solo_vale_si_hay_empate(self):
        with self.assertRaises(ValidationError) as caso:
            self._partido(2, 1, pl=5, pv=4).clean()
        self.assertIn("empatado", caso.exception.messages[0])

    def test_la_tanda_no_puede_quedar_igualada(self):
        with self.assertRaises(ValidationError) as caso:
            self._partido(1, 1, pl=3, pv=3).clean()
        self.assertIn("ganador", caso.exception.messages[0])

    def test_una_tanda_correcta_pasa(self):
        self._partido(1, 1, pl=5, pv=4).clean()

    def test_ganador_por_penales(self):
        self.assertEqual(self._partido(1, 1, pl=5, pv=4).ganador_por_penales(),
                         self.datos["equipo"])
        self.assertIsNone(self._partido(1, 1).ganador_por_penales())


class LaTandaDecideQuienPasaDeRonda(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _cuadro(self, nombre="Copa penales"):
        camp = _campeonato_para_calendario(
            nombre, self.datos["deporte"], ["LUNES", "MIERCOLES", "VIERNES"],
            tipo="ELIMINATORIA")
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_eliminatoria(camp.id)
        return camp

    def test_un_empate_con_tanda_avanza_solo(self):
        camp = self._cuadro()
        primera = list(Partido.objects.filter(campeonato=camp, ronda=1)
                       .order_by("fecha", "hora", "id"))
        ganadores = []
        for partido in primera:
            partido.resultado_local = 1
            partido.resultado_visitante = 1
            partido.penales_local = 5
            partido.penales_visitante = 3
            partido.estado = "FINALIZADO"
            partido.save()
            ganadores.append(partido.equipo_local_id)

        final = list(Partido.objects.filter(campeonato=camp, ronda=2))
        self.assertEqual(len(final), 1, "la tanda debe desbloquear la ronda")
        self.assertCountEqual(
            [final[0].equipo_local_id, final[0].equipo_visitante_id], ganadores,
            "deben pasar los ganadores de la tanda, no los locales por defecto")

    def test_pasa_el_visitante_si_gana_la_tanda(self):
        camp = self._cuadro("Copa visitante")
        primera = list(Partido.objects.filter(campeonato=camp, ronda=1))
        esperados = []
        for partido in primera:
            partido.resultado_local = 2
            partido.resultado_visitante = 2
            partido.penales_local = 2
            partido.penales_visitante = 4
            partido.estado = "FINALIZADO"
            partido.save()
            esperados.append(partido.equipo_visitante_id)

        final = Partido.objects.filter(campeonato=camp, ronda=2).first()
        self.assertCountEqual(
            [final.equipo_local_id, final.equipo_visitante_id], esperados)

    def test_sin_tanda_sigue_bloqueado(self):
        camp = self._cuadro("Copa bloqueada")
        for partido in Partido.objects.filter(campeonato=camp, ronda=1):
            partido.resultado_local = 1
            partido.resultado_visitante = 1
            partido.estado = "FINALIZADO"
            partido.save()
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 0)

    def test_anotar_la_tanda_despues_desbloquea(self):
        """El arbitro cierra el acta empatada y luego anota la tanda."""
        camp = self._cuadro("Copa tardia")
        primera = list(Partido.objects.filter(campeonato=camp, ronda=1))
        for partido in primera:
            partido.resultado_local = 0
            partido.resultado_visitante = 0
            partido.estado = "FINALIZADO"
            partido.save()
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 0)

        for partido in primera:
            partido.penales_local = 4
            partido.penales_visitante = 2
            partido.save()
        self.assertEqual(Partido.objects.filter(campeonato=camp, ronda=2).count(), 1)


class LaTandaNoAfectaALaTablaDePosiciones(PruebaBase):
    """Los penaltis no son goles: no deben sumar en la clasificacion."""

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_un_empate_con_tanda_sigue_siendo_empate_en_la_tabla(self):
        camp = _campeonato_para_calendario(
            "Liga con tanda", self.datos["deporte"], ["LUNES"])
        equipos = _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 2)

        Partido.objects.create(
            campeonato=camp, equipo_local=equipos[0], equipo_visitante=equipos[1],
            fecha=date.today(), hora=time(18, 0), lugar="Cancha 1",
            resultado_local=1, resultado_visitante=1,
            penales_local=5, penales_visitante=3, estado="FINALIZADO")

        tabla = calcular_tabla_posiciones(camp)
        for fila in tabla:
            self.assertEqual(fila["puntos"], 1, "un empate da 1 punto a cada uno")
            self.assertEqual(fila["gf"], 1, "los penaltis no cuentan como goles")
            self.assertEqual(fila["pe"], 1)
            self.assertEqual(fila["pg"], 0, "la tanda no convierte el empate en victoria")


class ElArbitroAnotaLaTandaDesdeElActa(PruebaBase):
    """El acta es la unica via enrutada para cerrar un partido.

    La URL registrar_resultado_partido apunta en realidad a
    acta_partido_arbitro; la funcion registrar_resultado_partido de
    arbitro_views no la enruta nadie.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def _partido_de_eliminatoria(self, nombre):
        camp = _campeonato_para_calendario(
            nombre, self.datos["deporte"], ["LUNES", "MIERCOLES"],
            tipo="ELIMINATORIA")
        _equipos_para_calendario(
            camp, self.datos["carrera"], self.datos["delegado"], 4)
        generar_fixture_eliminatoria(camp.id)
        partido = Partido.objects.filter(campeonato=camp, ronda=1).first()
        partido.arbitro = self.datos["arbitro"]
        partido.save()
        return partido

    def _enviar(self, partido, datos):
        # Los equipos de estos campeonatos no tienen jugadores, asi que la
        # suma de goles por jugador es 0 y el acta solo cuadra con un 0-0.
        self.client.force_login(self.datos["arbitro"].usuario)
        return self.client.post(
            reverse("registrar_resultado_partido", args=[partido.id]), datos)

    def test_guarda_la_tanda(self):
        partido = self._partido_de_eliminatoria("Acta tanda")
        self._enviar(partido, {"resultado_local": "0", "resultado_visitante": "0",
                               "penales_local": "5", "penales_visitante": "4"})
        partido.refresh_from_db()
        self.assertEqual((partido.penales_local, partido.penales_visitante), (5, 4))
        self.assertEqual(partido.estado, "FINALIZADO")

    def test_rechaza_una_tanda_igualada(self):
        partido = self._partido_de_eliminatoria("Acta igualada")
        self._enviar(partido, {"resultado_local": "0", "resultado_visitante": "0",
                               "penales_local": "3", "penales_visitante": "3"})
        partido.refresh_from_db()
        self.assertIsNone(partido.penales_local,
                          "una tanda igualada no debe guardarse")
        self.assertNotEqual(partido.estado, "FINALIZADO")

    def test_rechaza_penaltis_sin_empate(self):
        partido = self._partido_de_eliminatoria("Acta sin empate")
        self._enviar(partido, {"resultado_local": "1", "resultado_visitante": "0",
                               "penales_local": "5", "penales_visitante": "4"})
        partido.refresh_from_db()
        self.assertIsNone(partido.penales_local)

    def test_un_partido_normal_se_guarda_sin_tanda(self):
        """El flujo de siempre no debe cambiar."""
        partido = self._partido_de_eliminatoria("Acta normal")
        self._enviar(partido, {"resultado_local": "0", "resultado_visitante": "0"})
        partido.refresh_from_db()
        self.assertEqual(partido.estado, "FINALIZADO")
        self.assertIsNone(partido.penales_local)

    def test_el_acta_valida_la_tanda(self):
        from core.forms import ArbitroActaForm

        formulario = ArbitroActaForm(data={
            "resultado_local": "1", "resultado_visitante": "1",
            "penales_local": "3", "penales_visitante": "3"})
        self.assertFalse(formulario.is_valid())
        self.assertIn("penales_local", formulario.errors)

        correcto = ArbitroActaForm(data={
            "resultado_local": "1", "resultado_visitante": "1",
            "penales_local": "5", "penales_visitante": "3"})
        self.assertTrue(correcto.is_valid(), correcto.errors.as_text())



# ---------------------------------------------------------------------------
# Imports de las vistas.
#
# core/urls.py hacia `from .views import *` y core/views/__init__.py
# encadenaba otros dieciocho comodines. Cuando dos modulos definian una
# funcion con el mismo nombre, el ultimo importado se quedaba con el nombre
# y el otro dejaba de existir sin ningun aviso: asi quedaron inalcanzables
# detalle_equipo (jugador_views) y registrar_resultado_partido
# (arbitro_views), con aspecto de codigo en uso.
# ---------------------------------------------------------------------------


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


class SinNombresDeVistaDuplicados(PruebaBase):
    """Ningun nombre de vista debe estar definido en dos modulos.

    Con los imports explicitos un duplicado ya no rompe las rutas, pero
    sigue siendo una trampa: al leer urls.py no se ve cual de las dos se
    usa. Esta prueba lo corta antes de que llegue a main.
    """

    # Ya no hay excepciones: es_admin y es_admin_o_delegado estaban
    # declarados en cinco modulos cada uno y ahora viven en core/permisos.py.
    AUXILIARES_TOLERADOS = set()

    def test_ningun_nombre_en_dos_modulos(self):
        por_nombre = {}
        for nombre_modulo, modulo in _modulos_de_vistas():
            for nombre in _definidos_en(modulo):
                por_nombre.setdefault(nombre, []).append(nombre_modulo)

        duplicados = {
            nombre: modulos for nombre, modulos in por_nombre.items()
            if len(modulos) > 1 and nombre not in self.AUXILIARES_TOLERADOS
        }
        detalle = "; ".join(f"{n} en {', '.join(sorted(m))}"
                            for n, m in sorted(duplicados.items()))
        self.assertEqual(
            duplicados, {},
            "hay vistas con el mismo nombre en varios modulos, y al leer "
            f"urls.py no se ve cual se usa: {detalle}")


class UrlsNoUsaImportsComodin(PruebaBase):
    """urls.py debe decir de que modulo sale cada vista."""

    def test_sin_import_estrella(self):
        fuente = Path(__file__).resolve().parent / "urls.py"
        arbol = ast.parse(fuente.read_text(encoding="utf-8"))
        comodines = [
            nodo.module for nodo in ast.walk(arbol)
            if isinstance(nodo, ast.ImportFrom)
            and any(alias.name == "*" for alias in nodo.names)
        ]
        self.assertEqual(comodines, [],
                         f"urls.py no debe usar import *: {comodines}")

    def test_el_paquete_de_vistas_tampoco(self):
        fuente = Path(__file__).resolve().parent / "views" / "__init__.py"
        arbol = ast.parse(fuente.read_text(encoding="utf-8"))
        comodines = [
            nodo.module for nodo in ast.walk(arbol)
            if isinstance(nodo, ast.ImportFrom)
            and any(alias.name == "*" for alias in nodo.names)
        ]
        self.assertEqual(comodines, [],
                         f"core/views/__init__.py no debe reexportar con *: {comodines}")


class TodaVistaEnrutadaSigueSiendoLaMisma(PruebaBase):
    """Red de seguridad del cambio de imports.

    Fija la vista concreta que atiende las rutas donde antes hubo un
    nombre duplicado, para que un import mal puesto no las desvie sin que
    nadie se entere.
    """

    ESPERADO = {
        # Esta gano el sombreado historico y es la version reparada.
        "tabla_estadisticas": "core.views.jugador_views.tabla_estadisticas",
        # El nombre de url apunta al acta, no a la funcion homonima.
        "registrar_resultado_partido": "core.views.arbitro_views.acta_partido_arbitro",
        "detalle_equipo": "core.views.equipo_views.detalle_equipo",
    }

    def test_cada_ruta_resuelve_a_la_vista_esperada(self):
        for nombre, esperado in self.ESPERADO.items():
            with self.subTest(ruta=nombre):
                coincidencia = resolve(reverse(nombre, args=[1]))
                real = (f"{coincidencia.func.__module__}."
                        f"{coincidencia.func.__name__}")
                self.assertEqual(real, esperado)


class PermisosEnUnSoloSitio(PruebaBase):
    """es_admin estaba en cinco modulos y es_admin_o_delegado en otros cinco.

    No eran copias identicas: cuatro de los cinco es_admin hacian
    `user.rol == 'ADMIN'`, que lanza AttributeError con un usuario anonimo
    porque AnonymousUser no tiene `rol`. Solo no se notaba donde hubiera un
    @login_required por delante. Ahora hay una unica version, la segura.
    """

    def test_ningun_modulo_de_vistas_los_redefine(self):
        repetidos = []
        for nombre_modulo, modulo in _modulos_de_vistas():
            definidos = _definidos_en(modulo)
            for funcion in ("es_admin", "es_admin_o_delegado"):
                if funcion in definidos:
                    repetidos.append(f"{funcion} en {nombre_modulo}")
        self.assertEqual(repetidos, [],
                         "deben importarse de core.permisos: " + ", ".join(repetidos))

    def test_no_revientan_con_un_usuario_anonimo(self):
        """Es la diferencia entre un 500 y una redireccion al login."""
        from django.contrib.auth.models import AnonymousUser
        from core.permisos import es_admin, es_admin_o_delegado

        anonimo = AnonymousUser()
        self.assertFalse(es_admin(anonimo))
        self.assertFalse(es_admin_o_delegado(anonimo))
        self.assertFalse(es_admin(None))
        self.assertFalse(es_admin_o_delegado(None))

    def test_responden_bien_por_rol(self):
        from core.permisos import es_admin, es_admin_o_delegado

        datos = _datos_base()
        casos = {
            "admin": (datos["admin"], True, True),
            "delegado": (datos["delegado"], False, True),
            "arbitro": (datos["arbitro"].usuario, False, False),
            "jugador": (datos["jugador"].usuario, False, False),
        }
        for etiqueta, (usuario, admin, admin_o_delegado) in casos.items():
            with self.subTest(rol=etiqueta):
                self.assertIs(es_admin(usuario), admin)
                self.assertIs(es_admin_o_delegado(usuario), admin_o_delegado)

    def test_un_rol_desconocido_no_da_permisos(self):
        from core.permisos import es_admin, es_admin_o_delegado

        class Raro:
            is_authenticated = True
            rol = "INVENTADO"

        self.assertFalse(es_admin(Raro()))
        self.assertFalse(es_admin_o_delegado(Raro()))

    def test_un_usuario_sin_atributo_rol_no_da_permisos(self):
        from core.permisos import es_admin

        class SinRol:
            is_authenticated = True

        self.assertFalse(es_admin(SinRol()))


class SinComentariosDjangoDeVariasLineas(PruebaBase):
    """Django solo trata {# #} como comentario dentro de una misma linea.

    Repartido en varias, el texto se imprime en la pagina. Ya habia una
    comprobacion asi en el workflow de CI, pero no como prueba, asi que el
    fallo solo se veia despues de subir: para varias lineas hay que usar
    {% templatetag openblock %} comment {% templatetag closeblock %}.
    """

    def test_ninguna_plantilla_los_reparte(self):
        fugas = []
        for plantilla in sorted(RAIZ_PLANTILLAS.rglob("*.html")):
            texto = plantilla.read_text(encoding="utf-8")
            for numero, linea in enumerate(texto.splitlines(), 1):
                if linea.count("{#") != linea.count("#}"):
                    fugas.append(
                        f"{plantilla.relative_to(RAIZ_PLANTILLAS).as_posix()}:{numero}")
        self.assertEqual(fugas, [],
                         "comentarios {# #} repartidos en varias lineas: "
                         + ", ".join(fugas))
