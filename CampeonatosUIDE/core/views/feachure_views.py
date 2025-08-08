from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Campeonato, Partido
from django.db.models import Q

def calendar_view(request, campeonato_id):
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)
    genero = request.GET.get('genero', 'masculino')  # Default to masculino

    partidos = Partido.objects.filter(
        Q(campeonato=campeonato) & 
        (Q(equipo_local__genero=genero) | Q(equipo_visitante__genero=genero))
    ).order_by('fecha', 'hora')

    context = {
        'campeonato': campeonato,
        'partidos': partidos,
        'genero_seleccionado': genero,
    }
    return render(request, 'feachure/calendar.html', context)
