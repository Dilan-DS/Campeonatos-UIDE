"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


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

