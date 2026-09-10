from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from core.utils.tabla_posiciones import calcular_tabla_posiciones
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
def completar_perfil_jugador(request):
    # Asegurarse de que el usuario sea un jugador y no tenga un perfil de Jugador ya creado
    if not hasattr(request.user, 'rol') or request.user.rol != 'JUGADOR':
        messages.error(request, "Acceso denegado. Esta página es solo para jugadores.")
        return redirect('vista_inicio')

    if hasattr(request.user, 'jugador'):
        messages.info(request, "Tu perfil de jugador ya está completo.")
        return redirect('jugador_dashboard')

    if request.method == 'POST':
        form = JugadorForm(request.POST)
        if form.is_valid():
            jugador = form.save(commit=False)
            jugador.usuario = request.user  # Asignar el usuario actual al jugador
            jugador.save()
            messages.success(request, 'Perfil de jugador completado exitosamente.')
            return redirect('inicio_publico')
    else:
        form = JugadorForm()
    return render(request, 'jugador/completar_perfil.html', {'form': form})


@login_required
@user_passes_test(es_jugador)
def jugador_dashboard(request):
    try:
        jugador = Jugador.objects.select_related('equipo__campeonato').get(usuario=request.user)

        equipo = None
        campeonato = None
        upcoming_matches = []
        player_stats = None
        deporte_nombre = None
        team_rank = None
        team_points = None

        if jugador.equipo:
            equipo = jugador.equipo
            campeonato = equipo.campeonato

            # Obtener los próximos partidos del equipo del jugador
            upcoming_matches = Partido.objects.filter(
                Q(equipo_local=equipo) | Q(equipo_visitante=equipo),
                fecha__gte=timezone.now().date() # Partidos desde hoy en adelante
            ).order_by('fecha', 'hora')[:5] # Obtener los próximos 5 partidos

            if campeonato: # Check if campeonato exists before accessing its attributes
                
                
                if hasattr(equipo, 'puntos_totales'): # Check if puntos_totales exists
                    team_points = equipo.puntos_totales

        

        

        return render(request, 'dashboard/jugador.html', {
            'jugador': jugador,
            'equipo': equipo,
            'campeonato': campeonato,
            'upcoming_matches': upcoming_matches,
            'player_stats': player_stats,
            'deporte_nombre': deporte_nombre, # Pasar el nombre del deporte para la plantilla
            'team_rank': team_rank,
            'team_points': team_points # Use the potentially None team_points
        })
    except Jugador.DoesNotExist:
        messages.error(request, "No se encontró tu perfil de jugador.")
        return redirect('inicio_publico')


@user_passes_test(es_jugador)
def ver_estadisticas_jugador(request, jugador_id):
    jugador = get_object_or_404(Jugador, pk=jugador_id)
    # SAFE: equipo/campeonato pueden ser None
    equipo = getattr(jugador, "equipo", None)
    campeonato = getattr(equipo, "campeonato", None) if equipo else None

    # Prepara valores seguros por defecto
    estadisticas = None
    partidos = []
    goles = []
    tarjetas = []
    deporte_nombre = None # Initialize deporte_nombre

    if campeonato is None:
        # Jugador sin equipo -> no consultes nada que requiera campeonato
        messages.info(request, "Este jugador aún no está asignado a un equipo.")
        contexto = {
            "jugador": jugador,
            "equipo": None,
            "campeonato": None,
            "estadisticas": estadisticas,
            "partidos": partidos,
            "goles": goles,
            "tarjetas": tarjetas,
            "deporte_nombre": deporte_nombre, # Pass deporte_nombre
        }
        return render(request, "jugador/estadisticas.html", contexto)
    
    # Jugador con equipo/campeonato: deja la lógica existente, pero
    # TODAS las consultas que antes asumían campeonato deben protegerse.
    deporte_nombre = campeonato.deporte.nombre.upper()

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

    contexto = {
        "jugador": jugador,
        "equipo": equipo,
        "campeonato": campeonato,
        "estadisticas": estadisticas,
        "partidos": partidos, # These variables are not populated in the provided snippet, assuming they are handled elsewhere or not needed for this specific fix.
        "goles": goles,
        "tarjetas": tarjetas,
        "deporte_nombre": deporte_nombre,
    }
    return render(request, "jugador/estadisticas.html", contexto)


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
    """Tabla de posiciones resaltando el equipo del jugador.

    Esta vista sombrea a la homónima de estadisticas_views (core/views/
    __init__.py importa jugador_views después), así que es la que resuelve
    la ruta 'tabla_estadisticas'. Recorría los partidos equipo por equipo
    para acumular las cifras pero nunca llegaba a construir la tabla:
    referenciaba `tabla_ordenada`, que no existía, y la ruta respondía
    NameError.

    Ahora reutiliza calcular_tabla_posiciones -- el mismo cálculo que usan
    las otras tablas, con dos consultas en lugar de dos por equipo -- y
    sólo añade la posición del equipo del jugador.
    """
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)

    equipo_jugador = None
    jugador = Jugador.objects.filter(usuario=request.user).select_related('equipo').first()
    if jugador:
        equipo_jugador = jugador.equipo
    elif getattr(request.user, 'rol', '') == 'JUGADOR':
        messages.warning(request, "No encontramos tu perfil de jugador, así que no podemos resaltar tu equipo.")

    tabla_ordenada = calcular_tabla_posiciones(campeonato)

    posicion_equipo_jugador = None
    if equipo_jugador:
        for indice, fila in enumerate(tabla_ordenada, start=1):
            if fila['equipo'].id == equipo_jugador.id:
                posicion_equipo_jugador = indice
                break

    context = {
        'campeonato': campeonato,
        'tabla': tabla_ordenada,
        'equipo_jugador': equipo_jugador,
        'posicion_equipo_jugador': posicion_equipo_jugador,
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

