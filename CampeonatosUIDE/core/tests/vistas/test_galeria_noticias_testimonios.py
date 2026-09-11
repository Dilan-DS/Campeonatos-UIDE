"""CRUD de galeria, noticias y testimonios: mismo patron, sin tests propios
(66%-69% de cobertura real). Las tres vistas de listado son publicas; las
de crear/editar exigen ADMIN o DELEGADO; noticias ademas restringe borrar
solo a ADMIN (mas estricto que crear/editar).
"""
import io

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from core.tests.base import *  # noqa: F401,F403


def _imagen(nombre="foto.png"):
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), color=(0, 128, 255)).save(buffer, format="PNG")
    return SimpleUploadedFile(nombre, buffer.getvalue(), content_type="image/png")


class GaleriaDeImagenes(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_el_listado_es_publico(self):
        respuesta = self.client.get(reverse("listar_imagenes_galeria"))
        self.assertEqual(respuesta.status_code, 200)

    def test_un_anonimo_no_puede_registrar_una_imagen(self):
        antes = ImagenGaleria.objects.count()
        respuesta = self.client.post(
            reverse("registrar_imagen_galeria"),
            {"titulo": "Colada", "imagen": _imagen()})
        self.assertNotEqual(respuesta.status_code, 200)
        self.assertEqual(ImagenGaleria.objects.count(), antes)

    def test_un_delegado_registra_una_imagen(self):
        self.client.force_login(self.datos["delegado"])
        respuesta = self.client.post(
            reverse("registrar_imagen_galeria"),
            {"titulo": "Foto del torneo", "imagen": _imagen()})
        self.assertRedirects(respuesta, reverse("listar_imagenes_galeria"))
        self.assertTrue(ImagenGaleria.objects.filter(titulo="Foto del torneo").exists())

    def test_editar_actualiza_el_titulo(self):
        imagen = ImagenGaleria.objects.create(titulo="Original", imagen=_imagen())
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(
            reverse("editar_imagen_galeria", args=[imagen.id]),
            {"titulo": "Editado", "imagen": _imagen()})
        self.assertRedirects(respuesta, reverse("listar_imagenes_galeria"))
        imagen.refresh_from_db()
        self.assertEqual(imagen.titulo, "Editado")

    def test_eliminar_la_borra(self):
        imagen = ImagenGaleria.objects.create(titulo="Para borrar", imagen=_imagen())
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(reverse("eliminar_imagen_galeria", args=[imagen.id]))
        self.assertRedirects(respuesta, reverse("listar_imagenes_galeria"))
        self.assertFalse(ImagenGaleria.objects.filter(pk=imagen.id).exists())

    def test_un_jugador_no_puede_eliminar(self):
        imagen = ImagenGaleria.objects.create(titulo="Protegida", imagen=_imagen())
        self.client.force_login(self.datos["jugador"].usuario)
        self.client.post(reverse("eliminar_imagen_galeria", args=[imagen.id]))
        self.assertTrue(ImagenGaleria.objects.filter(pk=imagen.id).exists())


class NoticiasConBusquedaYPaginacion(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        for i in range(11):
            Noticia.objects.create(titulo=f"Noticia {i}", contenido=f"Contenido {i}")
        Noticia.objects.create(titulo="Partido especial", contenido="Cobertura especial.")

    def test_el_listado_pagina_de_a_nueve(self):
        respuesta = self.client.get(reverse("listar_noticias"))
        self.assertEqual(len(respuesta.context["page_obj"]), 9)
        self.assertTrue(respuesta.context["page_obj"].has_next())

    def test_la_busqueda_filtra_por_titulo_o_contenido(self):
        respuesta = self.client.get(reverse("listar_noticias"), {"q": "especial"})
        titulos = {n.titulo for n in respuesta.context["page_obj"]}
        self.assertEqual(titulos, {"Partido especial"})

    def test_un_anonimo_no_puede_crear_noticias(self):
        antes = Noticia.objects.count()
        self.client.post(reverse("registrar_noticia"), {"titulo": "Colada", "contenido": "x"})
        self.assertEqual(Noticia.objects.count(), antes)

    def test_un_delegado_puede_crear_y_editar(self):
        self.client.force_login(self.datos["delegado"])
        respuesta = self.client.post(
            reverse("registrar_noticia"), {"titulo": "Noticia del delegado", "contenido": "..."})
        self.assertRedirects(respuesta, reverse("listar_noticias"))
        noticia = Noticia.objects.get(titulo="Noticia del delegado")

        respuesta = self.client.post(
            reverse("editar_noticia", args=[noticia.id]),
            {"titulo": "Noticia editada", "contenido": "..."})
        self.assertRedirects(respuesta, reverse("listar_noticias"))
        noticia.refresh_from_db()
        self.assertEqual(noticia.titulo, "Noticia editada")

    def test_un_delegado_no_puede_eliminar_solo_el_admin(self):
        """EliminarNoticia exige ADMIN, mas estricto que crear/editar."""
        noticia = Noticia.objects.first()
        self.client.force_login(self.datos["delegado"])
        self.client.post(reverse("eliminar_noticia", args=[noticia.id]))
        self.assertTrue(Noticia.objects.filter(pk=noticia.id).exists())

    def test_el_admin_si_puede_eliminar(self):
        noticia = Noticia.objects.first()
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(reverse("eliminar_noticia", args=[noticia.id]))
        self.assertRedirects(respuesta, reverse("listar_noticias"))
        self.assertFalse(Noticia.objects.filter(pk=noticia.id).exists())


class Testimonios(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_el_listado_es_publico(self):
        respuesta = self.client.get(reverse("listar_testimonios"))
        self.assertEqual(respuesta.status_code, 200)

    def test_un_anonimo_no_puede_crear_un_testimonio(self):
        antes = Testimonio.objects.count()
        self.client.post(reverse("registrar_testimonio"), {"autor": "Alguien", "contenido": "..."})
        self.assertEqual(Testimonio.objects.count(), antes)

    def test_un_delegado_crea_edita_y_elimina(self):
        self.client.force_login(self.datos["delegado"])
        respuesta = self.client.post(
            reverse("registrar_testimonio"), {"autor": "Delegado", "contenido": "Buena experiencia."})
        self.assertRedirects(respuesta, reverse("listar_testimonios"))
        testimonio = Testimonio.objects.get(autor="Delegado")

        respuesta = self.client.post(
            reverse("editar_testimonio", args=[testimonio.id]),
            {"autor": "Delegado editado", "contenido": "Editado."})
        self.assertRedirects(respuesta, reverse("listar_testimonios"))
        testimonio.refresh_from_db()
        self.assertEqual(testimonio.autor, "Delegado editado")

        respuesta = self.client.post(reverse("eliminar_testimonio", args=[testimonio.id]))
        self.assertRedirects(respuesta, reverse("listar_testimonios"))
        self.assertFalse(Testimonio.objects.filter(pk=testimonio.id).exists())

    def test_un_jugador_no_puede_administrar_testimonios(self):
        testimonio = Testimonio.objects.create(autor="Protegido", contenido="...")
        self.client.force_login(self.datos["jugador"].usuario)
        self.client.post(
            reverse("editar_testimonio", args=[testimonio.id]),
            {"autor": "Hackeado", "contenido": "..."})
        testimonio.refresh_from_db()
        self.assertEqual(testimonio.autor, "Protegido")
