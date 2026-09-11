"""Suite de pruebas de core, organizada por categoria.

Este paquete reemplaza al antiguo core/tests.py (archivo unico). Los
fixtures y helpers compartidos por varias categorias viven en
`core.tests.base`; cada modulo test_*.py se enfoca en un tema concreto.
"""

from core.tests.base import *  # noqa: F401,F403


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

