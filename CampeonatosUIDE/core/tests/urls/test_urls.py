"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

import core as _core_pkg

from core.tests.base import *  # noqa: F401,F403

CORE_DIR = Path(_core_pkg.__file__).resolve().parent


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
        fuente = CORE_DIR / "urls.py"
        arbol = ast.parse(fuente.read_text(encoding="utf-8"))
        comodines = [
            nodo.module for nodo in ast.walk(arbol)
            if isinstance(nodo, ast.ImportFrom)
            and any(alias.name == "*" for alias in nodo.names)
        ]
        self.assertEqual(comodines, [],
                         f"urls.py no debe usar import *: {comodines}")

    def test_el_paquete_de_vistas_tampoco(self):
        fuente = CORE_DIR / "views" / "__init__.py"
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

