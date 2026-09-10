"""Pruebas de regresión de la auditoría de UI/UX.

Cada prueba fija un fallo concreto que se encontró en el proyecto, para que
no vuelva a colarse. La primera clase es un barrido: recorre todas las
rutas con nombre en cada rol y falla si alguna responde 5xx, que es como
se detectaron once vistas rotas.
"""
from datetime import date, time, timedelta

from django.test import TestCase, override_settings
from django.urls import NoReverseMatch, get_resolver, reverse
from django.urls.resolvers import URLPattern, URLResolver

from core.forms import ArbitroActaForm, RegistroUsuarioForm
from core.models import (
    Arbitro, Campeonato, Carrera, CodigoQR, Deporte, Equipo, ImagenGaleria,
    Jugador, Noticia, Pago, Partido, Suspension, Testimonio, Usuario,
)

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
