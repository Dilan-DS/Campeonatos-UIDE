from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Partido, Campeonato, Usuario, Equipo
from core.forms import PartidoForm
from core.views.admin_views import es_admin
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django import forms

# Función para validar que sea admin
def es_admin(user):
    return user.rol == 'ADMIN'

@login_required
@user_passes_test(es_admin)
def listar_partidos(request):
    # Obtiene todos los partidos registrados en la base de datos y los ordena por fecha y hora
    partidos = Partido.objects.all().order_by('-fecha', '-hora')
    # Renderiza la plantilla 'listar_partidos.html' con los partidos
    return render(request, 'partido/listar_partidos.html', {'partidos': partidos})


@login_required
@user_passes_test(es_admin)
def registrar_partido(request):
    raise PermissionDenied


@login_required
@user_passes_test(es_admin)
def detalle_partido(request, partido_id):
    # Obtiene el partido por su ID, o devuelve un error 404 si no se encuentra
    partido = get_object_or_404(Partido, id=partido_id)
    # Verifica si el partido tiene un campeonato asociado
    return render(request, 'partido/detalle_partido.html', {'partido': partido})


class PartidoAdminForm(forms.ModelForm):
    class Meta:
        model = Partido
        fields = ['fecha', 'hora', 'lugar', 'arbitro', 'estado']

@login_required
def editar_partido(request, partido_id):
    if getattr(request.user, 'rol', '').upper() != 'ADMIN':
        raise PermissionDenied
    
    partido = get_object_or_404(Partido, pk=partido_id)
    
    if request.method == 'POST':
        form = PartidoAdminForm(request.POST, instance=partido)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partido actualizado correctamente.')
            return redirect('calendario_global')
    else:
        form = PartidoAdminForm(instance=partido)

    # Re-render the calendar view with the form in context for the modal
    qs = Partido.objects.select_related(
        'campeonato', 'equipo_local', 'equipo_visitante', 'arbitro__usuario'
    ).order_by('fecha', 'hora')

    campeonato_id_filter = request.GET.get('campeonato')
    genero_filter = request.GET.get('genero')
    estado_filter = request.GET.get('estado')
    desde_filter = request.GET.get('desde')
    hasta_filter = request.GET.get('hasta')

    if campeonato_id_filter:
        qs = qs.filter(campeonato_id=campeonato_id_filter)
    if genero_filter in ('masculino', 'femenino'):
        qs = qs.filter(equipo_local__genero=genero_filter, equipo_visitante__genero=genero_filter)
    if estado_filter in ('PROGRAMADO', 'JUGADO', 'SUSPENDIDO'):
        qs = qs.filter(estado=estado_filter)
    if desde_filter:
        qs = qs.filter(fecha__gte=desde_filter)
    if hasta_filter:
        qs = qs.filter(fecha__lte=hasta_filter)

    contexto = {
        'partidos': qs,
        'campeonatos': Campeonato.objects.all().order_by('-id'),
        'form': form,
        'partido_a_editar': partido
    }
    return render(request, 'partido/calendario_global.html', contexto)

@login_required
@user_passes_test(es_admin)
def eliminar_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    
    if request.method == 'POST':
        partido.delete()
        messages.success(request, 'Partido eliminado correctamente.')
        return redirect('listar_partidos')
    
    return render(request, 'partido/eliminar_partido.html', {'partido': partido})


@login_required
@user_passes_test(es_admin)
def aplazar_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)

    if request.method == 'POST':
        form = PartidoForm(request.POST, instance=partido)
        if form.is_valid():
            nuevo_partido = form.save(commit=False)
            # Aquí podrías registrar el cambio o validar reglas de aplazamiento
            nuevo_partido.save()
            messages.success(request, 'Partido aplazado exitosamente.')
            return redirect('detalle_partido', partido_id=partido.id)
    else:
        form = PartidoForm(instance=partido)

    return render(request, 'partido/aplazar_partido.html', {'form': form, 'partido': partido})

@login_required
def fixture_campeonato_view(request, campeonato_id):
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)
    partidos_qs = Partido.objects.filter(campeonato=campeonato).order_by('fecha', 'hora')

    user_role = request.user.rol

    if user_role == 'ADMIN':
        partidos = partidos_qs
    elif user_role == 'DELEGADO':
        delegado_equipos = Equipo.objects.filter(delegado=request.user, campeonato=campeonato)
        if delegado_equipos.exists():
            partidos = partidos_qs.filter(Q(equipo_local__in=delegado_equipos) | Q(equipo_visitante__in=delegado_equipos))
        else:
            partidos = Partido.objects.none()
    elif user_role == 'JUGADOR':
        if hasattr(request.user, 'jugador') and request.user.jugador.equipo:
            jugador_equipo = request.user.jugador.equipo
            if jugador_equipo.campeonato == campeonato:
                partidos = partidos_qs.filter(Q(equipo_local=jugador_equipo) | Q(equipo_visitante=jugador_equipo))
            else:
                partidos = Partido.objects.none()
        else:
            partidos = Partido.objects.none()
    elif user_role == 'ARBITRO':
        if hasattr(request.user, 'arbitro'):
            arbitro_obj = request.user.arbitro
            partidos = partidos_qs.filter(arbitro=arbitro_obj)
        else:
            partidos = Partido.objects.none()
    else:
        partidos = Partido.objects.none()

    genero = request.GET.get('genero', 'masculino').lower()
    if genero not in ('masculino', 'femenino'):
        genero = 'masculino'

    partidos = partidos.filter(equipo_local__genero=genero, equipo_visitante__genero=genero)

    return render(request, 'feachure/calendar.html', {
        'campeonato': campeonato,
        'partidos': partidos,
        'genero_seleccionado': genero,
        'campeonato_sin_fixture': not partidos_qs.exists(),
    })

@login_required
def calendario_global_view(request):
    qs = Partido.objects.select_related(
        'campeonato', 'equipo_local', 'equipo_visitante', 'arbitro__usuario'
    ).order_by('fecha', 'hora')

    campeonato_id = request.GET.get('campeonato')
    genero = request.GET.get('genero')
    estado = request.GET.get('estado')
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    if campeonato_id:
        qs = qs.filter(campeonato_id=campeonato_id)
    if genero in ('masculino', 'femenino'):
        qs = qs.filter(equipo_local__genero=genero, equipo_visitante__genero=genero)
    if estado in ('PROGRAMADO', 'JUGADO', 'SUSPENDIDO'):
        qs = qs.filter(estado=estado)
    if desde:
        qs = qs.filter(fecha__gte=desde)
    if hasta:
        qs = qs.filter(fecha__lte=hasta)

    contexto = {
        'partidos': qs,
        'campeonatos': Campeonato.objects.all().order_by('-id')
    }
    return render(request, 'partido/calendario_global.html', contexto)