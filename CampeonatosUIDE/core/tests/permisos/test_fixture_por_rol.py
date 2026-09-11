"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


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

