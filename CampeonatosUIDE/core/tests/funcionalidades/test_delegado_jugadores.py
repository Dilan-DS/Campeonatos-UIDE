"""Reglas reales de delegado_views.py: alta de jugadores a un equipo.

Ninguna de estas rutas tenia test propio (69% y 51% de cobertura medida
con `coverage` en ListarJugadoresParaEquipoView y AgregarJugadorAEquipoView
respectivamente), pese a ser donde se decide quien puede jugar por un
equipo: exige pago aprobado, mismo genero, no duplicar inscripcion y
respetar el cupo maximo del campeonato.

Cada test usa su propio campeonato (en vez de reutilizar el de
_datos_base) para que el delegado tenga un unico equipo por campeonato:
Equipo.objects...first() no garantiza orden si hay mas de uno.
"""

from core.tests.base import *  # noqa: F401,F403


def _campeonato_y_equipo_aprobado(datos, nombre, genero="masculino"):
    campeonato = _campeonato_para_calendario(nombre, datos["deporte"], ["LUNES"])
    equipo = Equipo.objects.create(
        nombre=f"{nombre} FC", campeonato=campeonato, carrera=datos["carrera"],
        delegado=datos["delegado"], aprobado=True, genero=genero)
    Pago.objects.create(equipo=equipo, metodo="EFECTIVO", estado="APROBADO")
    return campeonato, equipo


class ListadoDeJugadoresDisponibles(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.campeonato, cls.equipo = _campeonato_y_equipo_aprobado(
            cls.datos, "Con pago aprobado")

    def _get(self, campeonato_id=None):
        params = {"campeonato_id": campeonato_id} if campeonato_id else {}
        return self.client.get(reverse("listar_jugadores_para_equipo"), params)

    def test_sin_equipo_propio_redirige_al_dashboard(self):
        ajeno = Usuario.objects.create_user(
            username="delegado_sin_equipo", email="dse@uide.edu.ec", password=PWD,
            rol="DELEGADO", carrera=self.datos["carrera"], genero="masculino")
        self.client.force_login(ajeno)
        respuesta = self._get()
        self.assertRedirects(respuesta, reverse("delegado_dashboard"))

    def test_sin_pago_aprobado_redirige_al_dashboard(self):
        """El equipo de _datos_base tiene un pago PENDIENTE, no APROBADO."""
        self.client.force_login(self.datos["delegado"])
        respuesta = self._get(self.datos["campeonato"].id)
        self.assertRedirects(respuesta, reverse("delegado_dashboard"))

    def test_con_pago_aprobado_lista_jugadores_del_mismo_genero(self):
        jugador_libre = Usuario.objects.create_user(
            username="jugador_libre", email="jl@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="masculino")
        jugadora_femenina = Usuario.objects.create_user(
            username="jugadora_femenina", email="jf@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="femenino")

        self.client.force_login(self.datos["delegado"])
        respuesta = self._get(self.campeonato.id)

        self.assertEqual(respuesta.status_code, 200)
        usuarios_listados = {d["usuario"].id for d in respuesta.context["jugadores_data"]}
        self.assertIn(jugador_libre.id, usuarios_listados)
        self.assertNotIn(jugadora_femenina.id, usuarios_listados,
                         "no debe mezclar generos distintos al del equipo")

    def test_marca_ya_inscrito_en_otro_equipo(self):
        self.client.force_login(self.datos["delegado"])
        respuesta = self._get(self.campeonato.id)
        fila = next(d for d in respuesta.context["jugadores_data"]
                    if d["usuario"].id == self.datos["jugador"].usuario_id)
        self.assertTrue(fila["ya_inscrito"])
        self.assertFalse(fila["es_mi_jugador"])


class AltaDeJugadorAEquipo(PruebaBase):

    @classmethod
    def setUpTestData(cls):
        cls.datos = _datos_base()
        cls.campeonato, cls.equipo = _campeonato_y_equipo_aprobado(
            cls.datos, "Receptor de altas")

    def setUp(self):
        self.client.force_login(self.datos["delegado"])

    def _agregar(self, jugador_usuario_id):
        return self.client.post(
            reverse("agregar_jugador_a_equipo", args=[jugador_usuario_id]),
            {"campeonato_id": self.campeonato.id})

    def test_un_no_delegado_no_puede_agregar(self):
        self.client.force_login(self.datos["jugador"].usuario)
        candidato = Usuario.objects.create_user(
            username="candidato", email="cand@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="masculino")
        respuesta = self.client.post(
            reverse("agregar_jugador_a_equipo", args=[candidato.id]),
            {"campeonato_id": self.campeonato.id})
        self.assertRedirects(respuesta, reverse("vista_inicio"))

    def test_sin_pago_aprobado_no_agrega_a_nadie(self):
        """Usa el campeonato de _datos_base, cuyo pago sigue PENDIENTE."""
        candidato = Usuario.objects.create_user(
            username="candidato2", email="cand2@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="masculino")
        Jugador.objects.create(usuario=candidato, edad=20)
        respuesta = self.client.post(
            reverse("agregar_jugador_a_equipo", args=[candidato.id]),
            {"campeonato_id": self.datos["campeonato"].id})
        # No se sigue el redirect: listar_jugadores_para_equipo encadena a
        # su vez a delegado_dashboard porque ese mismo pago sigue pendiente.
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, reverse("listar_jugadores_para_equipo"))
        candidato_jugador = Jugador.objects.get(usuario=candidato)
        self.assertIsNone(candidato_jugador.equipo_id)

    def test_usuario_sin_perfil_de_jugador_no_se_puede_agregar(self):
        """rol=JUGADOR pero sin fila en el modelo Jugador (perfil incompleto)."""
        sin_perfil = Usuario.objects.create_user(
            username="sin_perfil", email="sp@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="masculino")
        respuesta = self._agregar(sin_perfil.id)
        self.assertRedirects(respuesta, reverse("listar_jugadores_para_equipo"))
        self.assertFalse(Jugador.objects.filter(usuario=sin_perfil).exists())

    def test_agrega_correctamente_a_un_jugador_libre(self):
        usuario_libre = Usuario.objects.create_user(
            username="libre", email="libre@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="masculino")
        jugador_libre = Jugador.objects.create(usuario=usuario_libre, edad=20)

        respuesta = self._agregar(usuario_libre.id)

        jugador_libre.refresh_from_db()
        self.assertEqual(jugador_libre.equipo_id, self.equipo.id)
        self.assertRedirects(respuesta, reverse("listar_jugadores_para_equipo"))

    def test_no_se_puede_agregar_a_alguien_ya_inscrito_en_otro_equipo(self):
        # El jugador de _datos_base ya esta en self.datos["equipo"].
        self._agregar(self.datos["jugador"].usuario_id)
        self.datos["jugador"].refresh_from_db()
        self.assertEqual(self.datos["jugador"].equipo_id, self.datos["equipo"].id,
                         "no debe moverse de equipo por esta via")

    def test_respeta_el_cupo_maximo_del_campeonato(self):
        self.campeonato.max_jugadores_por_equipo = 1
        self.campeonato.save()
        primero = Usuario.objects.create_user(
            username="primero", email="primero@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="masculino")
        Jugador.objects.create(usuario=primero, edad=20, equipo=self.equipo)

        segundo = Usuario.objects.create_user(
            username="segundo", email="segundo@uide.edu.ec", password=PWD,
            rol="JUGADOR", carrera=self.datos["carrera"], genero="masculino")
        Jugador.objects.create(usuario=segundo, edad=20)

        self._agregar(segundo.id)

        self.assertEqual(self.equipo.jugadores.count(), 1,
                         "no debe superar max_jugadores_por_equipo")
