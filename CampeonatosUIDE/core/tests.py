"""Pruebas de regresión de la auditoría de UI/UX.

Cada prueba fija un fallo concreto que se encontró en el proyecto, para que
no vuelva a colarse. La primera clase es un barrido: recorre todas las
rutas con nombre en cada rol y falla si alguna responde 5xx, que es como
se detectaron once vistas rotas.
"""
import re
from datetime import date, time, timedelta
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import NoReverseMatch, get_resolver, reverse
from django.urls.resolvers import URLPattern, URLResolver

from core.forms import ArbitroActaForm, RegistroUsuarioForm
from core.models import (
    Arbitro, Campeonato, Carrera, CodigoQR, Deporte, Equipo, ImagenGaleria,
    Jugador, Noticia, Pago, Partido, Suspension, Testimonio, Usuario,
)
from core.utils.tabla_posiciones import calcular_tabla_posiciones

PWD = "Prueba.2026"


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
