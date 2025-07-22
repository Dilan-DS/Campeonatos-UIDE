from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import Jugador
from django.http import HttpResponse

def es_jugador(user):
    # Verifica si el usuario es un jugador
    return user.rol == 'JUGADOR'


@login_required
@user_passes_test(es_jugador)
# función para el dashboard del jugador
def jugador_dashboard(request):
    # Intenta obtener el jugador asociado al usuario actual
    try:
        # Utiliza select_related para optimizar la consulta y evitar consultas adicionales
        jugador = Jugador.objects.select_related('equipo__campeonato').get(usuario=request.user)
        # Si el jugador tiene un equipo y un campeonato, los incluye en el contexto
        equipo = jugador.equipo
        # Si el equipo tiene un campeonato, lo incluye en el contexto
        campeonato = equipo.campeonato
        # Renderiza la plantilla 'jugador.html' con el jugador, equipo y campeonato
        return render(request, 'dashboard/jugador.html', {
            'jugador': jugador,
            'equipo': equipo,
            'campeonato': campeonato
        })
    # Si no se encuentra el jugador, muestra un mensaje de error y redirige al inicio público
    except Jugador.DoesNotExist:
        messages.error(request, "No se encontró tu perfil de jugador.")

        return redirect('inicio_publico')

@user_passes_test(es_jugador)
def ver_estadisticas_jugador(request, jugador_id):
    # Esta vista es exclusiva para jugadores
    return HttpResponse(f"Estadísticas del jugador {jugador_id}")