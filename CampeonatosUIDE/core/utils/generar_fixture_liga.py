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

    equipos_aprobados = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True))

    if len(equipos_aprobados) < 2:
        print(f"No hay suficientes equipos aprobados para generar el fixture del campeonato {campeonato.nombre}.")
        return

    equipos_masculinos = [e for e in equipos_aprobados if e.genero == 'masculino']
    equipos_femeninos = [e for e in equipos_aprobados if e.genero == 'femenino']

    print(f"Generando fixture de liga (todos contra todos) para el campeonato: {campeonato.nombre}")

    def create_league_matches_for_gender_group(team_list, championship, start_date, end_date, valid_days_of_week):
        if len(team_list) < 2:
            print(f"No hay suficientes equipos en este grupo de género para generar partidos de liga.")
            return 0

        matches_created = 0
        current_date = start_date

        team_pairs = list(itertools.combinations(team_list, 2))

        for equipo1, equipo2 in team_pairs:
            while current_date <= end_date and current_date.strftime('%A').upper() not in [d.upper() for d in valid_days_of_week]:
                current_date += timedelta(days=1)

            if current_date > end_date:
                print("Advertencia: No hay suficientes días disponibles para programar todos los partidos.")
                break

            arbitros_disponibles = Arbitro.objects.all()
            arbitro_asignado = random.choice(arbitros_disponibles) if arbitros_disponibles.exists() else None

            try:
                with transaction.atomic():
                    Partido.objects.create(
                        campeonato=championship,
                        equipo_local=equipo1,
                        equipo_visitante=equipo2,
                        fecha=current_date,
                        hora=timezone.now().time(),
                        lugar="Cancha Principal",
                        arbitro=arbitro_asignado,
                        estado='PROGRAMADO'
                    )
                    matches_created += 1
                    print(f"Partido creado: {equipo1.nombre} vs {equipo2.nombre} el {current_date}. Árbitro: {arbitro_asignado.usuario.username if arbitro_asignado else 'No asignado'}")
            except Exception as e:
                print(f"Error al crear partido: {e}")

            current_date += timedelta(days=1)
        return matches_created

    total_matches_created = 0
    total_matches_created += create_league_matches_for_gender_group(equipos_masculinos, campeonato, campeonato.fecha_inicio, campeonato.fecha_fin, campeonato.dias_partido)
    total_matches_created += create_league_matches_for_gender_group(equipos_femeninos, campeonato, campeonato.fecha_inicio, campeonato.fecha_fin, campeonato.dias_partido)

    if total_matches_created == 0:
        print("No se pudieron crear partidos para la liga.")
    else:
        print(f"Fixture de liga generado para {campeonato.nombre}. Se crearon {total_matches_created} partidos.")
