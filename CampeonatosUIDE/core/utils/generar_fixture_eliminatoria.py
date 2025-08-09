from core.models import Campeonato, Equipo, Partido, Arbitro
from django.utils import timezone
from datetime import timedelta, time
import random
from django.core.exceptions import ValidationError

def generar_fixture_eliminatoria(campeonato_id):
    try:
        campeonato = Campeonato.objects.get(id=campeonato_id)
    except Campeonato.DoesNotExist:
        print(f"Campeonato con ID {campeonato_id} no encontrado.")
        return

    print(f"Generando fixture de ELIMINATORIA para: {campeonato.nombre}")

    # 1. Separar equipos por género
    equipos_masculinos = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True, genero='masculino'))
    equipos_femeninos = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True, genero='femenino'))

    def generar_ronda_eliminatoria(equipos, genero):
        creados = 0 # Contador de partidos creados
        if len(equipos) < 2:
            print(f"No hay suficientes equipos de género {genero} para generar el fixture.")
            return creados

        # 2. Manejo de número impar de equipos con BYE
        # En una eliminatoria, necesitamos que el número de participantes en la primera ronda sea una potencia de 2.
        # Los equipos con BYE pasan directamente a la siguiente ronda.
        num_equipos = len(equipos)
        next_power_of_2 = 2**((num_equipos - 1).bit_length())
        num_byes = next_power_of_2 - num_equipos
        
        equipos_con_bye = random.sample(equipos, num_byes)
        equipos_primera_ronda = [e for e in equipos if e not in equipos_con_bye]

        print(f"Género {genero}: {num_equipos} equipos -> {num_byes} BYEs, {len(equipos_primera_ronda)} equipos en 1ra ronda.")

        random.shuffle(equipos_primera_ronda)
        
        # Emparejar equipos para la primera ronda
        partidos_ronda = []
        for i in range(0, len(equipos_primera_ronda), 2):
            if i + 1 < len(equipos_primera_ronda):
                partidos_ronda.append((equipos_primera_ronda[i], equipos_primera_ronda[i+1]))

        # 3. Asignar fechas y crear partidos
        fecha_partido = campeonato.fecha_inicio
        
        # Mapeo explícito y robusto de días de la semana a números de weekday()
        DIAS_MAP = {
            'LUNES': 0, 'MARTES': 1, 'MIERCOLES': 2, 'JUEVES': 3, 
            'VIERNES': 4, 'SABADO': 5, 'DOMINGO': 6
        }
        dias_permitidos_num = [DIAS_MAP[d.upper()] for d in campeonato.dias_partido]

        for equipo1, equipo2 in partidos_ronda:
            while fecha_partido.weekday() not in dias_permitidos_num:
                fecha_partido += timedelta(days=1)

            if fecha_partido > campeonato.fecha_fin:
                print("ADVERTENCIA: Se ha superado la fecha de fin del campeonato.")
                break

            arbitros_disponibles = Arbitro.objects.filter(deportes=campeonato.deporte)
            arbitro = random.choice(list(arbitros_disponibles)) if arbitros_disponibles else None

            try:
                hora_partido = time(18, 0) # Usar una hora fija
                partido = Partido(
                    campeonato=campeonato,
                    equipo_local=equipo1,
                    equipo_visitante=equipo2,
                    fecha=fecha_partido,
                    hora=hora_partido,
                    lugar="Por definir",
                    arbitro=arbitro,
                    estado='PROGRAMADO'
                )
                partido.full_clean()
                partido.save()
                creados += 1
                print(f"CREADO: {equipo1.nombre} vs {equipo2.nombre} ({fecha_partido} {hora_partido})")
            except ValidationError as e:
                print(f"VALIDATION ERROR: {equipo1.nombre} vs {equipo2.nombre} el {fecha_partido}: {e.message_dict}")
            except Exception as e:
                print(f"ERROR inesperado: {equipo1.nombre} vs {equipo2.nombre} el {fecha_partido}: {e}")
            
            fecha_partido += timedelta(days=1)
        return creados

    total_creados = 0
    total_creados += generar_ronda_eliminatoria(equipos_masculinos, 'masculino')
    total_creados += generar_ronda_eliminatoria(equipos_femeninos, 'femenino')
    
    print(f"Fixture de eliminatoria generado para {campeonato.nombre}. Total partidos creados: {total_creados}")
    return total_creados