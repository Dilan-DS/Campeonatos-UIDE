from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import Partido, Usuario, Arbitro, Campeonato, Equipo # Import Arbitro for request.user.arbitro
from django.db.models import Q # For select_related if needed
from django.contrib import messages # For messages framework

# Permisos helpers
def es_admin(user):
    return user.is_authenticated and getattr(user, "rol", "") == "ADMIN"

def es_arbitro(user):
    return user.is_authenticated and getattr(user, "rol", "") == "ARBITRO"

# FBV listar_arbitros (ADMIN)
@login_required
@user_passes_test(es_admin, login_url='/login/')
def listar_arbitros(request):
    arbitros = Arbitro.objects.all().select_related('usuario')
    return render(request, 'arbitro/listar.html', {'arbitros': arbitros})

# FBV mis_partidos_arbitro (ÁRBITRO)
@login_required
@user_passes_test(es_arbitro, login_url='/login/')
def mis_partidos_arbitro(request):
    try:
        # Asegurarse de que request.user.arbitro exista y sea el objeto Arbitro
        # Si el campo arbitro en Partido es FK a Usuario, usar request.user directamente
        # Si es FK a Arbitro, usar request.user.arbitro
        # Asumiendo que Partido.arbitro es FK a Arbitro, y Arbitro tiene OneToOne a Usuario
        arbitro_obj = request.user.arbitro
        partidos = (
            Partido.objects
            .filter(arbitro=arbitro_obj)
            .select_related('equipo_local','equipo_visitante','campeonato')
            .order_by('fecha','hora','id')
        )
        return render(request, 'arbitro/mis_partidos.html', {'partidos': partidos})
    except Arbitro.DoesNotExist:
        messages.error(request, "No estás registrado como árbitro o tu perfil de árbitro no está completo.")
        return redirect('vista_inicio') # Redirigir a una página segura

# FBV registrar_resultado_partido (ÁRBITRO)
@login_required
@user_passes_test(es_arbitro, login_url='/login/')
def registrar_resultado_partido(request, partido_id):
    try:
        arbitro_obj = request.user.arbitro
        partido = get_object_or_404(Partido, pk=partido_id, arbitro=arbitro_obj) # Ensure arbitro matches
    except Arbitro.DoesNotExist:
        messages.error(request, "No estás registrado como árbitro o tu perfil de árbitro no está completo.")
        return redirect('vista_inicio')

    if request.method == 'POST':
        partido.resultado_local = int(request.POST.get('resultado_local', 0))
        partido.resultado_visitante = int(request.POST.get('resultado_visitante', 0))
        partido.estado = 'FINALIZADO'
        partido.save()
        messages.success(request, "Resultado registrado correctamente y partido finalizado.")
        return redirect('mis_partidos_arbitro')
    
    return render(request, 'arbitro/registrar_resultado.html', {'partido': partido})

# FBV disciplinario_partido (ÁRBITRO)
@login_required
@user_passes_test(es_arbitro, login_url='/login/')
def disciplinario_partido(request, partido_id):
    try:
        arbitro_obj = request.user.arbitro
        partido = get_object_or_404(Partido, pk=partido_id, arbitro=arbitro_obj) # Ensure arbitro matches
    except Arbitro.DoesNotExist:
        messages.error(request, "No estás registrado como árbitro o tu perfil de árbitro no está completo.")
        return redirect('vista_inicio')

    if request.method == 'POST':
        # Asumiendo campos en el modelo Partido o un modelo relacionado
        partido.tarjetas_amarillas_local = int(request.POST.get('tarjetas_amarillas_local', 0))
        partido.tarjetas_amarillas_visitante = int(request.POST.get('tarjetas_amarillas_visitante', 0))
        partido.tarjetas_rojas_local = int(request.POST.get('tarjetas_rojas_local', 0))
        partido.tarjetas_rojas_visitante = int(request.POST.get('tarjetas_rojas_visitante', 0))
        partido.observaciones_arbitro = request.POST.get('observaciones_arbitro', '')
        # suspensiones_json: Esto requeriría más lógica para parsear JSON o un formato específico
        # Por ahora, solo guardamos las observaciones.
        partido.save()
        messages.success(request, "Datos disciplinarios registrados correctamente.")
        return redirect('mis_partidos_arbitro')
    
    return render(request, 'arbitro/disciplinario.html', {'partido': partido})

@login_required
@user_passes_test(es_arbitro, login_url='/login/')
def ver_tabla_posiciones_arbitro(request, campeonato_id):
    campeonato = get_object_or_404(Campeonato, pk=campeonato_id)
    equipos = Equipo.objects.filter(campeonato=campeonato)
    
    tabla = []
    for equipo in equipos:
        partidos_local = Partido.objects.filter(equipo_local=equipo, estado='FINALIZADO')
        partidos_visitante = Partido.objects.filter(equipo_visitante=equipo, estado='FINALIZADO')

        pj = partidos_local.count() + partidos_visitante.count()
        pg = 0
        pe = 0
        pp = 0
        gf = 0
        gc = 0

        for partido in partidos_local:
            if partido.resultado_local > partido.resultado_visitante:
                pg += 1
            elif partido.resultado_local == partido.resultado_visitante:
                pe += 1
            else:
                pp += 1
            gf += partido.resultado_local or 0
            gc += partido.resultado_visitante or 0

        for partido in partidos_visitante:
            if partido.resultado_visitante > partido.resultado_local:
                pg += 1
            elif partido.resultado_visitante == partido.resultado_local:
                pe += 1
            else:
                pp += 1
            gf += partido.resultado_visitante or 0
            gc += partido.resultado_local or 0
            
        puntos = (pg * 3) + (pe * 1)
        gd = gf - gc

        tabla.append({
            'equipo': equipo,
            'pj': pj,
            'pg': pg,
            'pe': pe,
            'pp': pp,
            'gf': gf,
            'gc': gc,
            'gd': gd,
            'puntos': puntos,
        })

    tabla.sort(key=lambda x: (x['puntos'], x['gd']), reverse=True)

    return render(request, 'campeonato/tabla_posiciones.html', {
        'campeonato': campeonato,
        'tabla': tabla
    })