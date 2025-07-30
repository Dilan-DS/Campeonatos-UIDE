from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import Jugador, Partido, Equipo, Campeonato
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


def es_jugador(user):
    return hasattr(user, 'rol') and user.rol == 'JUGADOR'


@login_required
@user_passes_test(es_jugador)
def jugador_dashboard(request):
    try:
        jugador = Jugador.objects.select_related('equipo__campeonato').get(usuario=request.user)
        equipo = jugador.equipo
        campeonato = equipo.campeonato
        return render(request, 'dashboard/jugador.html', {
            'jugador': jugador,
            'equipo': equipo,
            'campeonato': campeonato
        })
    except Jugador.DoesNotExist:
        messages.error(request, "No se encontró tu perfil de jugador.")
        return redirect('inicio_publico')


@user_passes_test(es_jugador)
def ver_estadisticas_jugador(request, jugador_id):
    jugador = get_object_or_404(Jugador, id=jugador_id, usuario=request.user)
    estadisticas = {
        'partidos_jugados': 10,
        'goles': 5,
        'asistencias': 3,
    }
    return render(request, 'jugador/estadisticas.html', {
        'jugador': jugador,
        'estadisticas': estadisticas,
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
    equipos = campeonato.equipo_set.all().order_by('-puntos', '-goles_favor')

    return render(request, 'campeonato/tabla_estadisticas.html', {
        'campeonato': campeonato,
        'equipos': equipos,
    })


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
