from core.models import Campeonato, Equipo, Partido, Arbitro
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import itertools
import random

def generar_fixture_liga(campeonato_id):
    try:
        campeonato = Campeonato.objects.get(id=campeonato_id)
    except Campeonato.DoesNotExist:
        print(f"Campeonato con ID {campeonato_id} no encontrado.")
        return

    # 1. Separar equipos por género
    equipos_masculinos = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True, genero='masculino'))
    equipos_femeninos = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True, genero='femenino'))

    print(f"Generando fixture de LIGA para: {campeonato.nombre}")
    print(f"Días de partido permitidos: {campeonato.dias_partido}")

    # Función interna para generar partidos para un grupo de género
    def generar_partidos_por_genero(equipos, genero):
        if len(equipos) < 2:
            print(f"No hay suficientes equipos de género {genero} para generar un fixture.")
            return

        # 2. Manejo de número impar de equipos con BYE
        if len(equipos) % 2 != 0:
            equipos.append(None)  # 'None' representa el BYE

        jornadas = []
        equipos_rotando = list(equipos[1:])
        
        for i in range(len(equipos) - 1):
            jornada_actual = []
            # Emparejar el primer equipo con el último de la lista rotativa
            if equipos[0] and equipos_rotando[-1]:
                jornada_actual.append((equipos[0], equipos_rotando[-1]))
            
            # Emparejar el resto de equipos
            for j in range(len(equipos_rotando) // 2):
                if equipos_rotando[j] and equipos_rotando[-(j + 2)]:
                    jornada_actual.append((equipos_rotando[j], equipos_rotando[-(j + 2)]))
            
            jornadas.append(jornada_actual)
            
            # Rotar la lista de equipos (excepto el primero)
            equipos_rotando.insert(0, equipos_rotando.pop())

        # 3. Asignar fechas y crear partidos
        fecha_partido = campeonato.fecha_inicio
        
        # Mapeo explícito y robusto de días de la semana a números de weekday()
        DIAS_MAP = {
            'LUNES': 0, 'MARTES': 1, 'MIERCOLES': 2, 'JUEVES': 3, 
            'VIERNES': 4, 'SABADO': 5, 'DOMINGO': 6
        }
        dias_permitidos_num = [DIAS_MAP[d.upper()] for d in campeonato.dias_partido]

        for jornada in jornadas:
            # Avanzar hasta encontrar un día de la semana permitido
            while fecha_partido.weekday() not in dias_permitidos_num:
                fecha_partido += timedelta(days=1)

            if fecha_partido > campeonato.fecha_fin:
                print("ADVERTENCIA: Se ha superado la fecha de fin del campeonato. No se pueden programar más partidos.")
                break

            for equipo1, equipo2 in jornada:
                if equipo1 and equipo2:  # Asegurarse de que no es un BYE
                    arbitros_disponibles = Arbitro.objects.filter(deportes=campeonato.deporte)
                    arbitro = random.choice(list(arbitros_disponibles)) if arbitros_disponibles else None
                    
                    Partido.objects.create(
                        campeonato=campeonato,
                        equipo_local=equipo1,
                        equipo_visitante=equipo2,
                        fecha=fecha_partido,
                        hora=timezone.now().time(),  # Puedes ajustar la hora
                        lugar="Por definir",
                        arbitro=arbitro,
                        estado='PROGRAMADO'
                    )
                    print(f"Partido Creado ({genero}): {equipo1.nombre} vs {equipo2.nombre} el {fecha_partido}")

            fecha_partido += timedelta(days=1)

    # Generar partidos para ambos géneros
    generar_partidos_por_genero(equipos_masculinos, 'masculino')
    generar_partidos_por_genero(equipos_femeninos, 'femenino')

    print(f"Fixture de liga generado exitosamente para {campeonato.nombre}.")
