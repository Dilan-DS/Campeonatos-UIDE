from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse

from core.models import Equipo, Campeonato
from core.forms import EquipoForm, PagoForm

# ========================
# EQUIPOS
# ======================== 

def es_admin_o_delegado(user):
    return user.rol in ['ADMIN', 'DELEGADO']

@login_required
@user_passes_test(es_admin_o_delegado)
def registrar_equipo(request):
    campeonato_id = request.GET.get('campeonato_id')
    campeonato = get_object_or_404(Campeonato, id=campeonato_id) if campeonato_id else None

    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            equipo = form.save()
            messages.success(request, 'Equipo registrado correctamente.')
            
            # Redirección robusta usando el nombre de la URL
            redirect_url = reverse('listar_equipos') + f'?campeonato_id={equipo.campeonato.id}'
            if request.user.rol == 'ADMIN':
                return redirect('registrar_pago_para_equipo_admin', equipo_id=equipo.id)
            return redirect(redirect_url)
    else:
        initial_data = {}
        if campeonato:
            initial_data['campeonato'] = campeonato
        form = EquipoForm(initial=initial_data)

    return render(request, 'equipo/registrar_equipo.html', {
        'form': form,
        'campeonato': campeonato
    })

@login_required
@user_passes_test(es_admin_o_delegado)
def listar_equipos(request):
    campeonato_id = request.GET.get('campeonato_id')
    campeonato = get_object_or_404(Campeonato, id=campeonato_id) if campeonato_id else None

    if campeonato:
        equipos = list(Equipo.objects.filter(campeonato=campeonato))
    else:
        equipos = list(Equipo.objects.all())
    equipos.sort(key=lambda e: e.puntos_totales or 0, reverse=True)

    return render(request, 'equipo/listar_equipos.html', {
        'equipos': equipos,
        'campeonato': campeonato  # ✅ Esto permite que el template lo use
    })

@login_required
@user_passes_test(es_admin_o_delegado)
def detalle_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    return render(request, 'equipo/registrar_equipo.html', {
        'equipo': equipo,
        'form': EquipoForm(instance=equipo),
        'ver': True
    })

@login_required
@user_passes_test(es_admin_o_delegado)
def editar_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    form = EquipoForm(request.POST or None, request.FILES or None, instance=equipo)
    if form.is_valid():
        form.save()
        messages.success(request, 'Equipo actualizado correctamente.')
        return redirect('detalle_equipo', id=equipo.id)
    return render(request, 'equipo/registrar_equipo.html', {
        'form': form,
        'equipo': equipo,
        'editar': True
    })

@login_required
@user_passes_test(es_admin_o_delegado)
def pago_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    form = PagoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        pago = form.save(commit=False)
        pago.equipo = equipo
        pago.save()
        messages.success(request, 'Pago registrado correctamente.')
        return redirect('detalle_equipo', id=equipo.id)
    return render(request, 'equipo/pago_equipo.html', {'form': form, 'equipo': equipo})

@login_required
@user_passes_test(es_admin_o_delegado)
def jugadores_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    jugadores = equipo.jugador_set.all()
    return render(request, 'equipo/jugadores_equipo.html', {'equipo': equipo, 'jugadores': jugadores})

@login_required
@user_passes_test(es_admin_o_delegado)
def eliminar_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    if request.method == 'POST':
        equipo.delete()
        messages.success(request, 'Equipo eliminado correctamente.')
        return redirect('listar_equipos')
    return render(request, 'equipo/confirmar_eliminacion.html', {'equipo': equipo})
