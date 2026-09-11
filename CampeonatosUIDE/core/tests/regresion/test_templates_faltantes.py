"""Vistas que renderizaban una plantilla que no existia en el repo.

`TodasLasRutasResponden` no detectaba estos casos porque prueba las rutas
con datos minimos: si no existe ninguna Transmision con pk=1, la vista
devuelve 404 antes de llegar al render() que hubiera reventado con
TemplateDoesNotExist. Aqui se crea el objeto real para forzar ese camino.

`eliminar_partido` y `aplazar_partido` (partido_views.py) tenian el mismo
problema y ademas no estaban enrutadas en core/urls.py ni enlazadas desde
ninguna plantilla. Ya se conectaron (path() en core/urls.py + botones en
partido/listar_partidos.html), asi que se prueban por HTTP real como
cualquier otra vista, no con RequestFactory.
"""
from core.tests.base import *  # noqa: F401,F403


class DetalleDeTransmisionRenderizaConDatosReales(PruebaBase):
    """Bug real: la fila "Ver" del listado de transmisiones apuntaba a
    esta vista y no existia core/templates/transmision/detalle_transmision.html.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.transmision = Transmision.objects.create(
            campeonato=cls.datos["campeonato"], partido=cls.datos["partido"],
            enlace="https://youtube.com/watch?v=abc123",
            descripcion="Transmisión de prueba.", activa=True)

    def test_la_pagina_de_detalle_responde_200(self):
        respuesta = self.client.get(reverse("detalle_transmision", args=[self.transmision.id]))
        self.assertEqual(respuesta.status_code, 200)

    def test_muestra_el_enlace_y_la_descripcion(self):
        respuesta = self.client.get(reverse("detalle_transmision", args=[self.transmision.id]))
        cuerpo = respuesta.content.decode()
        self.assertIn(self.transmision.enlace, cuerpo)
        self.assertIn("Transmisión de prueba.", cuerpo)

    def test_el_listado_enlaza_a_una_pagina_que_existe(self):
        """El link 'Ver' de listar_transmisiones.html debe seguir funcionando."""
        respuesta = self.client.get(reverse("listar_transmisiones"), follow=False)
        self.assertEqual(respuesta.status_code, 200)
        enlace_detalle = reverse("detalle_transmision", args=[self.transmision.id])
        self.assertIn(enlace_detalle, respuesta.content.decode())
        self.assertEqual(self.client.get(enlace_detalle).status_code, 200)


class EliminarYAplazarPartidoYaEstanConectadas(PruebaBase):
    """Se enrutaron en core/urls.py y se enlazaron desde listar_partidos.html.

    Un admin ahora puede de verdad eliminar o aplazar un partido desde la
    interfaz; antes el codigo existia pero era inalcanzable.
    """

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_el_listado_enlaza_a_ambas_acciones(self):
        self.client.force_login(self.datos["admin"])
        cuerpo = self.client.get(reverse("listar_partidos")).content.decode()
        self.assertIn(reverse("eliminar_partido", args=[self.datos["partido"].id]), cuerpo)
        self.assertIn(reverse("aplazar_partido", args=[self.datos["partido"].id]), cuerpo)

    def test_get_eliminar_partido_muestra_confirmacion_sin_borrar(self):
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(reverse("eliminar_partido", args=[self.datos["partido"].id]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(Partido.objects.filter(pk=self.datos["partido"].id).exists())

    def test_post_eliminar_partido_lo_borra(self):
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(reverse("eliminar_partido", args=[self.datos["partido"].id]))
        self.assertRedirects(respuesta, reverse("listar_partidos"))
        self.assertFalse(Partido.objects.filter(pk=self.datos["partido"].id).exists())

    def test_un_delegado_no_puede_eliminar_un_partido(self):
        self.client.force_login(self.datos["delegado"])
        self.client.post(reverse("eliminar_partido", args=[self.datos["partido"].id]))
        self.assertTrue(Partido.objects.filter(pk=self.datos["partido"].id).exists())

    def test_get_aplazar_partido_muestra_el_formulario(self):
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(reverse("aplazar_partido", args=[self.datos["partido"].id]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("form", respuesta.context)

    def test_post_aplazar_partido_cambia_la_fecha(self):
        self.client.force_login(self.datos["admin"])
        partido = self.datos["partido"]
        nueva_fecha = partido.fecha + timedelta(days=7)
        respuesta = self.client.post(
            reverse("aplazar_partido", args=[partido.id]),
            {"campeonato": partido.campeonato_id, "equipo_local": partido.equipo_local_id,
             "equipo_visitante": partido.equipo_visitante_id, "fecha": nueva_fecha,
             "hora": partido.hora, "lugar": partido.lugar, "estado": partido.estado})
        self.assertRedirects(respuesta, reverse("detalle_partido", args=[partido.id]))
        partido.refresh_from_db()
        self.assertEqual(partido.fecha, nueva_fecha)

    def test_un_delegado_no_puede_aplazar_un_partido(self):
        self.client.force_login(self.datos["delegado"])
        partido = self.datos["partido"]
        fecha_original = partido.fecha
        self.client.post(
            reverse("aplazar_partido", args=[partido.id]),
            {"campeonato": partido.campeonato_id, "equipo_local": partido.equipo_local_id,
             "equipo_visitante": partido.equipo_visitante_id,
             "fecha": partido.fecha + timedelta(days=7),
             "hora": partido.hora, "lugar": partido.lugar, "estado": partido.estado})
        partido.refresh_from_db()
        self.assertEqual(partido.fecha, fecha_original)
