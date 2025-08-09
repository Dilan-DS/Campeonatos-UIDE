from core.models import Campeonato, Equipo, Partido, Arbitro
from django.utils import timezone
from datetime import timedelta, time
import random
import itertools
from django.core.exceptions import ValidationError

def generar_fixture_fase_grupos(campeonato_id, num_grupos=4):
    try:
        campeonato = Campeonato.objects.get(id=campeonato_id)
    except Campeonato.DoesNotExist:
        print(f"Campeonato con ID {campeonato_id} no encontrado.")
        return

    print(f"Generando fixture de FASE DE GRUPOS para: {campeonato.nombre}")

    # 1. Separar equipos por género
    equipos_masculinos = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True, genero='masculino'))
    equipos_femeninos = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True, genero='femenino'))

    def generar_partidos_por_genero(equipos, genero):
        if len(equipos) < num_grupos:
            print(f"No hay suficientes equipos de género {genero} para formar {num_grupos} grupos.")
            return

        random.shuffle(equipos)
        
        # 2. Distribuir equipos en grupos
        grupos = [[] for _ in range(num_grupos)]
        for i, equipo in enumerate(equipos):
            grupos[i % num_grupos].append(equipo)

        # 3. Generar partidos para cada grupo (formato liga dentro del grupo)
        fecha_partido = campeonato.fecha_inicio
        
        # Mapeo explícito y robusto de días de la semana a números de weekday()
        DIAS_MAP = {
            'LUNES': 0, 'MARTES': 1, 'MIERCOLES': 2, 'JUEVES': 3, 
            'VIERNES': 4, 'SABADO': 5, 'DOMINGO': 6
        }
        dias_permitidos_num = [DIAS_MAP[d.upper()] for d in campeonato.dias_partido]

        for i, grupo in enumerate(grupos):
            print(f"--- Generando partidos para el Grupo {i+1} ({genero}) ---")
            if len(grupo) < 2:
                continue

            # Manejo de BYE si el grupo tiene número impar de equipos
            if len(grupo) % 2 != 0:
                grupo.append(None) # Añadir un placeholder para el BYE

            enfrentamientos = list(itertools.combinations(grupo, 2))

            for equipo1, equipo2 in enfrentamientos:
                if not equipo1 or not equipo2: # Omitir si es un BYE
                    continue

                while fecha_partido.weekday() not in dias_permitidos_num:
                    fecha_partido += timedelta(days=1)

                if fecha_partido > campeonato.fecha_fin:
                    print("ADVERTENCIA: Se ha superado la fecha de fin del campeonato.")
                    break

                arbitros_disponibles = Arbitro.objects.filter(deportes=campeonato.deporte)
                arbitro = random.choice(list(arbitros_disponibles)) if arbitros_disponibles else None

                try:
                    # Usar una hora fija para los partidos, por ejemplo, las 18:00
                    hora_partido = time(18, 0)
                    
                    partido = Partido(
                        campeonato=campeonato,
                        equipo_local=equipo1,
                        equipo_visitante=equipo2,
                        fecha=fecha_partido,
                        hora=hora_partido,
                        lugar=f"Cancha Grupo {i+1}",
                        arbitro=arbitro,
                        estado='PROGRAMADO'
                    )
                    partido.full_clean() # Ejecutar validaciones del modelo
                    partido.save() # Guardar el partido si las validaciones pasan
                    print(f"Partido Creado (Grupo {i+1}, {genero}): {equipo1.nombre} vs {equipo2.nombre} el {fecha_partido}")
                except ValidationError as e:
                    print(f"ERROR de Validación al crear partido (Grupo {i+1}, {genero}) {equipo1.nombre} vs {equipo2.nombre} el {fecha_partido}: {e.message_dict}")
                except Exception as e:
                    print(f"ERROR inesperado al crear partido (Grupo {i+1}, {genero}) {equipo1.nombre} vs {equipo2.nombre} el {fecha_partido}: {e}")
                
                fecha_partido += timedelta(days=1)

    generar_partidos_por_genero(equipos_masculinos, 'masculino')
    generar_partidos_por_genero(equipos_femeninos, 'femenino')

    print(f"Fixture de fase de grupos generado para {campeonato.nombre}.")