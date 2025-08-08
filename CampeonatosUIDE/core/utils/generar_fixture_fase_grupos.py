from core.models import Campeonato, Equipo, Partido, Arbitro
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import random

def generar_fixture_fase_grupos(campeonato_id):
    try:
        campeonato = Campeonato.objects.get(id=campeonato_id)
    except Campeonato.DoesNotExist:
        print(f"Campeonato con ID {campeonato_id} no encontrado.")
        return

    equipos_aprobados = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True))

    if len(equipos_aprobados) < 2:
        print(f"No hay suficientes equipos aprobados para generar el fixture del campeonato {campeonato.nombre}.")
        return

    equipos_masculinos = [e for e in equipos_aprobados if e.genero == 'masculino']
    equipos_femeninos = [e for e in equipos_aprobados if e.genero == 'femenino']

    print(f"Generando fixture de fase de grupos para el campeonato: {campeonato.nombre}")

    def create_matches_for_gender_group(team_list, championship, start_date, end_date, valid_days_of_week):
        if len(team_list) < 2:
            print(f"No hay suficientes equipos en este grupo de género para generar partidos.")
            return 0

        matches_created = 0
        current_date = start_date

        # Simple placeholder for group stage fixture generation
        # This needs to be replaced with actual group stage logic (e.g., round-robin within groups)
        # For now, it will just create one match between the first two teams as an example.
        equipo1 = team_list[0]
        equipo2 = team_list[1]

        # Ensure the match date is within the championship's date range
        match_date = championship.fecha_inicio
        if match_date > championship.fecha_fin:
            match_date = championship.fecha_fin # Fallback if start date is already past end date

        # Find a valid day for the match
        current_date = match_date
        while current_date.strftime('%A').upper() not in [d.upper() for d in valid_days_of_week]:
            current_date += timedelta(days=1)
            if current_date > championship.fecha_fin:
                print("No hay días disponibles para programar partidos dentro del rango del campeonato.")
                return 0

        arbitros_disponibles = Arbitro.objects.all()
        arbitro_asignado = random.choice(arbitros_disponibles) if arbitros_disponibles.exists() else None

        try:
            with transaction.atomic():
                Partido.objects.create(
                    campeonato=championship,
                    equipo_local=equipo1,
                    equipo_visitante=equipo2,
                    fecha=current_date,
                    hora=timezone.now().time(), # Use current time as a placeholder
                    lugar="Cancha Principal", # Placeholder
                    arbitro=arbitro_asignado,
                    estado='PROGRAMADO'
                )
                matches_created += 1
                print(f"Partido creado: {equipo1.nombre} vs {equipo2.nombre} el {current_date}. Árbitro: {arbitro_asignado.usuario.username if arbitro_asignado else 'No asignado'}")
        except Exception as e:
            print(f"Error al crear partido: {e}")
        return matches_created

    total_matches_created = 0
    total_matches_created += create_matches_for_gender_group(equipos_masculinos, campeonato, campeonato.fecha_inicio, campeonato.fecha_fin, campeonato.dias_partido)
    total_matches_created += create_matches_for_gender_group(equipos_femeninos, campeonato, campeonato.fecha_inicio, campeonato.fecha_fin, campeonato.dias_partido)

    print(f"Fixture de fase de grupos generado (ejemplo) para {campeonato.nombre}. Total de partidos creados: {total_matches_created}.")
