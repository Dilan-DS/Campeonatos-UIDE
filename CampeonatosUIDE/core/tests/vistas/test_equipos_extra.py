"""Huecos reales de equipo_views.py (76% de cobertura medida).

Se enfoca en lo que TestEquipos.py (vistas/test_equipos.py, ya existente)
no cubria: el calculo de estadisticas por deporte en ver_equipo_jugador
y jugadores_equipo, el filtrado de listar_equipos por rol, el alta real
con EquipoForm, y el bloqueo de un delegado editando el equipo de otro.
"""
from core.tests.base import *  # noqa: F401,F403


class VerEquipoComoJugador(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_un_jugador_sin_perfil_es_redirigido(self):
        sin_perfil = Usuario.objects.create_user(
            username="sin_perfil_ver", email="spv@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="masculino")
        self.client.force_login(sin_perfil)
        respuesta = self.client.get(
            reverse("ver_equipo_jugador", args=[self.datos["equipo"].id]))
        # No se sigue el redirect: jugador_dashboard encadena a su vez a
        # completar_perfil_jugador porque este usuario tampoco tiene Jugador.
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, reverse("jugador_dashboard"))

    def test_un_jugador_solo_ve_su_propio_equipo_aunque_pida_otro(self):
        otro_equipo = Equipo.objects.create(
            nombre="Equipo ajeno", campeonato=self.datos["campeonato"],
            carrera=self.datos["carrera"], delegado=self.datos["delegado"], aprobado=True)
        self.client.force_login(self.datos["jugador"].usuario)
        respuesta = self.client.get(reverse("ver_equipo_jugador", args=[otro_equipo.id]))
        self.assertEqual(respuesta.context["equipo"], self.datos["equipo"])

    def test_muestra_las_estadisticas_de_futbol_del_jugador(self):
        EstadisticaJugadorFutbol.objects.create(
            campeonato=self.datos["campeonato"], jugador=self.datos["jugador"], goles=3)
        self.client.force_login(self.datos["jugador"].usuario)
        respuesta = self.client.get(
            reverse("ver_equipo_jugador", args=[self.datos["equipo"].id]))
        fila = next(d for d in respuesta.context["jugadores_data"]
                    if d["jugador"] == self.datos["jugador"])
        self.assertEqual(fila["stats"].goles, 3)
        self.assertEqual(fila["deporte_nombre"], "FÚTBOL")


class ListadoDeEquiposPorRol(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_el_delegado_solo_ve_sus_propios_equipos(self):
        otro_delegado = Usuario.objects.create_user(
            username="otro_delegado_listado", email="odl@uide.edu.ec", password=PWD,
            rol="DELEGADO", carrera=self.datos["carrera"], genero="masculino")
        Equipo.objects.create(
            nombre="Equipo del otro delegado", campeonato=self.datos["campeonato"],
            carrera=self.datos["carrera"], delegado=otro_delegado, aprobado=True)

        self.client.force_login(self.datos["delegado"])
        respuesta = self.client.get(reverse("listar_equipos"))
        for equipo in respuesta.context["equipos"]:
            self.assertEqual(equipo.delegado_id, self.datos["delegado"].id)

    def test_el_admin_ve_todos_los_equipos_del_campeonato(self):
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(
            reverse("listar_equipos"), {"campeonato_id": self.datos["campeonato"].id})
        nombres = {e.nombre for e in respuesta.context["equipos"]}
        self.assertIn(self.datos["equipo"].nombre, nombres)


class AltaYEdicionDeEquipo(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_un_delegado_registra_un_equipo(self):
        """Equipo.clean() exige un campeonato en estado INSCRIPCION."""
        campeonato_abierto = _campeonato_para_calendario(
            "Abierto a inscripciones", self.datos["deporte"], ["LUNES"])
        self.client.force_login(self.datos["delegado"])
        respuesta = self.client.post(reverse("registrar_equipo"), {
            "nombre": "Equipo Nuevo FC", "campeonato": campeonato_abierto.pk,
            "carrera": self.datos["carrera"].pk, "delegado": self.datos["delegado"].pk,
            "genero": "masculino", "logo": _imagen_valida(),
        })
        self.assertRedirects(respuesta, reverse("listar_equipos"))
        self.assertTrue(Equipo.objects.filter(nombre="Equipo Nuevo FC").exists())

    def test_un_delegado_no_puede_editar_el_equipo_de_otro(self):
        otro_delegado = Usuario.objects.create_user(
            username="otro_delegado_editar", email="ode@uide.edu.ec", password=PWD,
            rol="DELEGADO", carrera=self.datos["carrera"], genero="masculino")
        self.client.force_login(otro_delegado)
        respuesta = self.client.post(
            reverse("editar_equipo", args=[self.datos["equipo"].id]),
            {"nombre": "Hackeado", "campeonato": self.datos["campeonato"].pk,
             "carrera": self.datos["carrera"].pk, "delegado": otro_delegado.pk,
             "genero": "masculino"})
        self.assertEqual(respuesta.status_code, 403)
        self.datos["equipo"].refresh_from_db()
        self.assertNotEqual(self.datos["equipo"].nombre, "Hackeado")

    def test_editar_no_permite_que_el_delegado_se_autoapruebe(self):
        self.datos["equipo"].aprobado = False
        self.datos["equipo"].save()
        self.client.force_login(self.datos["delegado"])
        self.client.post(
            reverse("editar_equipo", args=[self.datos["equipo"].id]),
            {"nombre": self.datos["equipo"].nombre, "campeonato": self.datos["campeonato"].pk,
             "carrera": self.datos["carrera"].pk, "delegado": self.datos["delegado"].pk,
             "genero": "masculino", "aprobado": "on"})
        self.datos["equipo"].refresh_from_db()
        self.assertFalse(self.datos["equipo"].aprobado,
                         "aprobado no debe poder cambiarse desde el formulario del delegado")


class JugadoresDelEquipoYDelDelegado(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_jugadores_equipo_bloqueado_si_no_esta_aprobado(self):
        self.datos["equipo"].aprobado = False
        self.datos["equipo"].save()
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(reverse("jugadores_equipo", args=[self.datos["equipo"].id]))
        self.assertRedirects(respuesta, reverse("detalle_equipo", args=[self.datos["equipo"].id]))

    def test_jugadores_equipo_muestra_estadisticas_si_esta_aprobado(self):
        EstadisticaJugadorFutbol.objects.create(
            campeonato=self.datos["campeonato"], jugador=self.datos["jugador"], goles=5)
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(reverse("jugadores_equipo", args=[self.datos["equipo"].id]))
        self.assertEqual(respuesta.status_code, 200)
        fila = respuesta.context["jugadores_data"][0]
        self.assertEqual(fila["stats"].goles, 5)

    def test_mis_jugadores_delegado_sin_equipo_redirige_al_dashboard(self):
        sin_equipo = Usuario.objects.create_user(
            username="delegado_sin_equipo_mjd", email="dsemjd@uide.edu.ec", password=PWD,
            rol="DELEGADO", carrera=self.datos["carrera"], genero="masculino")
        self.client.force_login(sin_equipo)
        respuesta = self.client.get(reverse("mis_jugadores_delegado"))
        self.assertRedirects(respuesta, reverse("delegado_dashboard"))

    def test_mis_jugadores_delegado_muestra_su_equipo(self):
        self.client.force_login(self.datos["delegado"])
        respuesta = self.client.get(
            reverse("mis_jugadores_delegado"), {"campeonato_id": self.datos["campeonato"].id})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["equipo"], self.datos["equipo"])


class EliminacionDeEquipo(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_get_no_borra_solo_redirige(self):
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(reverse("eliminar_equipo", args=[self.datos["equipo"].id]))
        self.assertRedirects(respuesta, reverse("listar_equipos"))
        self.assertTrue(Equipo.objects.filter(pk=self.datos["equipo"].id).exists())

    def test_post_elimina_el_equipo(self):
        equipo = Equipo.objects.create(
            nombre="Desechable", campeonato=self.datos["campeonato"],
            carrera=self.datos["carrera"], delegado=self.datos["delegado"])
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.post(reverse("eliminar_equipo", args=[equipo.id]))
        self.assertRedirects(respuesta, reverse("listar_equipos"))
        self.assertFalse(Equipo.objects.filter(pk=equipo.id).exists())


class WrapperDePagoEquipo(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()

    def test_redirige_al_flujo_canonico_de_pagos(self):
        self.client.force_login(self.datos["admin"])
        respuesta = self.client.get(reverse("pago_equipo", args=[self.datos["equipo"].id]))
        self.assertRedirects(
            respuesta, reverse("registrar_pago_equipo", args=[self.datos["equipo"].id]))
