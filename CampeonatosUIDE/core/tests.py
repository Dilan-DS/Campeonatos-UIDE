from datetime import date, time

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from core.models import Campeonato, Carrera, Deporte, Equipo, Usuario, Partido
from core.utils.tabla_posiciones import calcular_tabla_posiciones


class TablaPosicionesQueryTest(TestCase):
    def setUp(self):
        carrera = Carrera.objects.create(nombre="Carrera de prueba")
        deporte = Deporte.objects.create(nombre="FUTBOL")
        delegado = Usuario.objects.create_user(
            username="delegado_prueba",
            email="delegado@example.test",
            password="contraseña-segura",
            rol="DELEGADO",
            carrera=carrera,
            genero="masculino",
        )
        self.campeonato = Campeonato.objects.create(
            nombre="Campeonato de prueba",
            tipo_campeonato="LIGA",
            descripcion="Prueba de consultas",
            fecha_inicio=date(2026, 1, 1),
            fecha_fin=date(2026, 1, 30),
            deporte=deporte,
            delegado=delegado,
        )
        self.local = Equipo.objects.create(
            campeonato=self.campeonato,
            nombre="Local",
            carrera=carrera,
            delegado=delegado,
            aprobado=True,
            genero="masculino",
        )
        self.visitante = Equipo.objects.create(
            campeonato=self.campeonato,
            nombre="Visitante",
            carrera=carrera,
            delegado=delegado,
            aprobado=True,
            genero="masculino",
        )
        Partido.objects.create(
            campeonato=self.campeonato,
            equipo_local=self.local,
            equipo_visitante=self.visitante,
            fecha=date(2026, 1, 2),
            hora=time(18, 0),
            lugar="Cancha de prueba",
            resultado_local=2,
            resultado_visitante=1,
            estado="FINALIZADO",
        )

    def test_calcula_tabla_con_dos_consultas_y_mantiene_resultados(self):
        with CaptureQueriesContext(connection) as queries:
            tabla = calcular_tabla_posiciones(self.campeonato)

        self.assertEqual(len(queries), 2)
        self.assertEqual([fila["equipo"] for fila in tabla], [self.local, self.visitante])
        self.assertEqual(tabla[0]["puntos"], 3)
        self.assertEqual(tabla[0]["gf"], 2)
        self.assertEqual(tabla[1]["pp"], 1)
