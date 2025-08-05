from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from core.models import (
    Jugador,
    Partido,
    Equipo,
    Campeonato,
    Usuario,
    EstadisticaJugadorFutbol,
    EstadisticaJugadorBasquet,
    EstadisticaJugadorAjedrez,
    EstadisticaJugadorEcuaboly,
    EstadisticaJugadorPingPong,
    EstadisticaJugadorTenis,
    EstadisticaJugadorVideojuegos,
    EstadisticaJugadorFutbolin
)
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from core.models import (
    Jugador,
    Partido,
    Equipo,
    Campeonato,
    Usuario,
    EstadisticaJugadorFutbol,
    EstadisticaJugadorBasquet,
    EstadisticaJugadorAjedrez,
    EstadisticaJugadorEcuaboly,
    EstadisticaJugadorPingPong,
    EstadisticaJugadorTenis,
    EstadisticaJugadorVideojuegos,
    EstadisticaJugadorFutbolin
)
from core.forms import JugadorForm, UsuarioForm


def es_delegado(user):
    return hasattr(user, 'rol') and user.rol == 'DELEGADO'

def es_jugador(user):
    return hasattr(user, 'rol') and user.rol == 'JUGADOR'


@login_required
@user_passes_test(es_delegado)
def registrar_jugador(request):
    if request.method == 'POST':
        form = JugadorForm(request.POST)
        if form.is_valid():
            jugador = form.save(commit=False)
            # Assuming the delegate is registering a player for their own team
            # You might need to adjust this logic based on how you want to assign players to teams
            # For now, let's assume the form handles team selection or it's implicitly handled.
            jugador.save()
            messages.success(request, 'Jugador registrado correctamente.')
            return redirect('listar_jugadores_para_equipo') # Redirect to the list of players for the delegate's team
    else:
        form = JugadorForm()
    return render(request, 'jugador/registrar_jugador.html', {'form': form})


@login_required
@user_passes_test(es_jugador)
def jugador_dashboard(request):
    try:
        jugador = Jugador.objects.select_related('equipo__campeonato').get(usuario=request.user)
        equipo = jugador.equipo
        campeonato = equipo.campeonato

        # Obtener los próximos partidos del equipo del jugador
        upcoming_matches = Partido.objects.filter(
            Q(equipo_local=equipo) | Q(equipo_visitante=equipo),
            fecha__gte=timezone.now().date() # Partidos desde hoy en adelante
        ).order_by('fecha', 'hora')[:5] # Obtener los próximos 5 partidos

        # Obtener las estadísticas del jugador según el deporte
        deporte_nombre = campeonato.deporte.nombre.upper()
        player_stats = None
        if deporte_nombre == 'FUTBOL':
            player_stats = EstadisticaJugadorFutbol.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == 'BASQUET':
            player_stats = EstadisticaJugadorBasquet.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == 'AJEDREZ':
            player_stats = EstadisticaJugadorAjedrez.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == 'ECUABOLY':
            player_stats = EstadisticaJugadorEcuaboly.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == 'PING PONG':
            player_stats = EstadisticaJugadorPingPong.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == 'TENIS':
            player_stats = EstadisticaJugadorTenis.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == 'VIDEOJUEGOS':
            player_stats = EstadisticaJugadorVideojuegos.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == 'FUTBOLIN':
            player_stats = EstadisticaJugadorFutbolin.objects.filter(jugador=jugador, campeonato=campeonato).first()

        # Calcular la posición del equipo del jugador en la tabla (duplicando lógica de TablaPosiciones para mostrar en dashboard)
        all_teams = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True))
        team_stats_for_ranking = []
        for t in all_teams:
            pj = 0; pg = 0; pe = 0; pp = 0; gf = 0; gc = 0; puntos = 0

            partidos_local = Partido.objects.filter(
                campeonato=campeonato,
                equipo_local=t,
                estado='FINALIZADO'
            )
            for p in partidos_local:
                pj += 1
                gf += p.resultado_local
                gc += p.resultado_visitante
                if p.resultado_local > p.resultado_visitante:
                    pg += 1
                    puntos += 3
                elif p.resultado_local == p.resultado_visitante:
                    pe += 1
                    puntos += 1
                else:
                    pp += 1

            partidos_visitante = Partido.objects.filter(
                campeonato=campeonato,
                equipo_visitante=t,
                estado='FINALIZADO'
            )
            for p in partidos_visitante:
                pj += 1
                gf += p.resultado_visitante
                gc += p.resultado_local
                if p.resultado_visitante > p.resultado_local:
                    pg += 1
                    puntos += 3
                elif p.resultado_visitante == p.resultado_local:
                    pe += 1
                    puntos += 1
                else:
                    pp += 1
            
            gd = gf - gc

            team_stats_for_ranking.append({
                'equipo': t,
                'pj': pj, 'pg': pg, 'pe': pe, 'pp': pp,
                'gf': gf, 'gc': gc, 'gd': gd, 'puntos': puntos
            })
        
        sorted_teams_for_ranking = sorted(team_stats_for_ranking, key=lambda x: (x['puntos'], x['gd'], x['gf']), reverse=True)

        team_rank = None
        for i, team_data in enumerate(sorted_teams_for_ranking):
            if team_data['equipo'] == equipo:
                team_rank = i + 1
                break

        return render(request, 'dashboard/jugador.html', {
            'jugador': jugador,
            'equipo': equipo,
            'campeonato': campeonato,
            'upcoming_matches': upcoming_matches,
            'player_stats': player_stats,
            'deporte_nombre': deporte_nombre, # Pasar el nombre del deporte para la plantilla
            'team_rank': team_rank,
            'team_points': equipo.puntos_totales # Asumiendo que esta propiedad ya existe y es eficiente
        })
    except Jugador.DoesNotExist:
        messages.error(request, "No se encontró tu perfil de jugador.")
        return redirect('inicio_publico')


@user_passes_test(es_jugador)
def ver_estadisticas_jugador(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id, usuario=request.user)
    equipo = jugador.equipo
    campeonato = equipo.campeonato
    deporte_nombre = campeonato.deporte.nombre.upper()

    estadisticas = None

    if deporte_nombre == 'FUTBOL':
        estadisticas = EstadisticaJugadorFutbol.objects.filter(jugador=jugador, campeonato=campeonato).first()
    elif deporte_nombre == 'BASQUET':
        estadisticas = EstadisticaJugadorBasquet.objects.filter(jugador=jugador, campeonato=campeonato).first()
    elif deporte_nombre == 'AJEDREZ':
        estadisticas = EstadisticaJugadorAjedrez.objects.filter(jugador=jugador, campeonato=campeonato).first()
    elif deporte_nombre == 'ECUABOLY':
        estadisticas = EstadisticaJugadorEcuaboly.objects.filter(jugador=jugador, campeonato=campeonato).first()
    elif deporte_nombre == 'PING PONG':
        estadisticas = EstadisticaJugadorPingPong.objects.filter(jugador=jugador, campeonato=campeonato).first()
    elif deporte_nombre == 'TENIS':
        estadisticas = EstadisticaJugadorTenis.objects.filter(jugador=jugador, campeonato=campeonato).first()
    elif deporte_nombre == 'VIDEOJUEGOS':
        estadisticas = EstadisticaJugadorVideojuegos.objects.filter(jugador=jugador, campeonato=campeonato).first()
    elif deporte_nombre == 'FUTBOLIN':
        estadisticas = EstadisticaJugadorFutbolin.objects.filter(jugador=jugador, campeonato=campeonato).first()

    return render(request, 'jugador/estadisticas.html', {
        'jugador': jugador,
        'estadisticas': estadisticas,
        'deporte_nombre': deporte_nombre
    })


@login_required
@user_passes_test(es_jugador)
def ver_mis_partidos(request):
    try:
        jugador = Jugador.objects.get(usuario=request.user)
    except ObjectDoesNotExist:
        messages.error(request, "No tienes un perfil de jugador asociado.")
        return redirect('inicio_publico')

    equipo = jugador.equipo
    partidos = Partido.objects.filter(
        Q(equipo_local=equipo) | Q(equipo_visitante=equipo)
    ).order_by('fecha', 'hora')

    return render(request, 'partido/mis_partidos_jugador.html', {'partidos': partidos})


@login_required
@user_passes_test(es_jugador)
def tabla_estadisticas(request, campeonato_id):
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)
    
    try:
        jugador = Jugador.objects.get(usuario=request.user)
        equipo_jugador = jugador.equipo
    except Jugador.DoesNotExist:
        equipo_jugador = None
        messages.warning(request, "No se encontró tu perfil de jugador. No se podrá resaltar tu equipo.")

    equipos = Equipo.objects.filter(campeonato=campeonato, aprobado=True)

    tabla = []
    for equipo in equipos:
        pj = 0  # Partidos Jugados
        pg = 0  # Partidos Ganados
        pe = 0  # Partidos Empatados
        pp = 0  # Partidos Perdidos
        gf = 0  # Goles a Favor
        gc = 0  # Goles en Contra
        puntos = 0

        # Partidos como local
        partidos_local = Partido.objects.filter(
            campeonato=campeonato,
            equipo_local=equipo,
            estado='FINALIZADO'
        )
        for p in partidos_local:
            pj += 1
            gf += p.resultado_local
            gc += p.resultado_visitante
            if p.resultado_local > p.resultado_visitante:
                pg += 1
                puntos += 3
            elif p.resultado_local == p.resultado_visitante:
                pe += 1
                puntos += 1
            else:
                pp += 1

        # Partidos como visitante
        partidos_visitante = Partido.objects.filter(
            campeonato=campeonato,
            equipo_visitante=equipo,
            estado='FINALIZADO'
        )
        for p in partidos_visitante:
            pj += 1
            gf += p.resultado_visitante
            gc += p.resultado_local
            if p.resultado_visitante > p.resultado_local:
                pg += 1
                puntos += 3
            elif p.resultado_visitante == p.resultado_local:
                pe += 1
                puntos += 1
            else:
                pp += 1
            
            gd = gf - gc

            team_stats_for_ranking.append({
                'equipo': t,
                'pj': pj, 'pg': pg, 'pe': pe, 'pp': pp,
                'gf': gf, 'gc': gc, 'gd': gd, 'puntos': puntos
            })
        
        sorted_teams_for_ranking = sorted(team_stats_for_ranking, key=lambda x: (x['puntos'], x['gd'], x['gf']), reverse=True)

        team_rank = None
        for i, team_data in enumerate(sorted_teams_for_ranking):
            if team_data['equipo'] == equipo:
                team_rank = i + 1
                break

    context = {
        'campeonato': campeonato,
        'tabla': tabla_ordenada,
        'equipo_jugador': equipo_jugador,
        'posicion_equipo_jugador': posicion_equipo_jugador
    }
    return render(request, 'campeonato/tabla_estadisticas.html', context)


@login_required
@user_passes_test(es_jugador)
def detalle_equipo(request, id):
    jugador = get_object_or_404(Jugador, usuario=request.user)
    equipo = get_object_or_404(Equipo, id=id)

    if jugador.equipo != equipo:
        messages.error(request, "No tienes permiso para ver ese equipo.")
        return redirect('jugador_dashboard')

    jugadores = equipo.jugadores.all()  # Cambia 'jugadores' si tu related_name es otro

    context = {
        'equipo': equipo,
        'jugadores': jugadores,
    }
    return render(request, 'equipo/detalle_equipo.html', context)

