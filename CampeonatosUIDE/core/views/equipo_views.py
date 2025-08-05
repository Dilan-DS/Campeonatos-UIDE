from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse

from core.models import (
    Equipo, Campeonato, Jugador, 
    EstadisticaJugadorFutbol, EstadisticaJugadorBasquet, EstadisticaJugadorAjedrez,
    EstadisticaJugadorEcuaboly, EstadisticaJugadorPingPong, EstadisticaJugadorTenis,
    EstadisticaJugadorVideojuegos, EstadisticaJugadorFutbolin
)
from core.forms import EquipoForm, PagoForm

@login_required
def ver_equipo_jugador(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    # Si el usuario es un jugador, obtenemos su equipo
    if request.user.rol == 'JUGADOR':
        try:
            jugador = Jugador.objects.get(usuario=request.user)
            equipo = jugador.equipo
        except Jugador.DoesNotExist:
            messages.error(request, "No estás registrado en ningún equipo.")
            return redirect('jugador_dashboard')

    jugadores_data = []
    campeonato = equipo.campeonato
    for jugador_item in equipo.jugadores.all():
        player_stats = None
        deporte_nombre = campeonato.deporte.nombre.upper()

        if deporte_nombre == 'FUTBOL':
            player_stats = EstadisticaJugadorFutbol.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == 'BASQUET':
            player_stats = EstadisticaJugadorBasquet.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == 'AJEDREZ':
            player_stats = EstadisticaJugadorAjedrez.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == 'ECUABOLY':
            player_stats = EstadisticaJugadorEcuaboly.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == 'PING PONG':
            player_stats = EstadisticaJugadorPingPong.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == 'TENIS':
            player_stats = EstadisticaJugadorTenis.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == 'VIDEOJUEGOS':
            player_stats = EstadisticaJugadorVideojuegos.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == 'FUTBOLIN':
            player_stats = EstadisticaJugadorFutbolin.objects.filter(jugador=jugador_item, campeonato=campeonato).first()

        jugadores_data.append({
            'jugador': jugador_item,
            'stats': player_stats,
            'deporte_nombre': deporte_nombre,
            'posicion': jugador_item.posicion,
        })

    return render(request, 'equipo/jugadores_equipo.html', {
        'equipo': equipo, 
        'jugadores_data': jugadores_data,
        'is_jugador_view': True,
    })

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
            # Obtener el campeonato del formulario
            campeonato_seleccionado = form.cleaned_data.get('campeonato')

            # Verificar el estado del campeonato antes de guardar el equipo
            if campeonato_seleccionado and campeonato_seleccionado.estado != 'INSCRIPCION':
                messages.error(request, f"El campeonato '{campeonato_seleccionado.nombre}' no está en estado de inscripción.")
                return render(request, 'equipo/registrar_equipo.html', {
                    'form': form,
                    'campeonato': campeonato_seleccionado # Pass the selected championship back to the template
                })

            equipo = form.save(commit=False)
            # Asignar el delegado actual al equipo
            equipo.delegado = request.user
            equipo.save()
            messages.success(request, 'Equipo registrado correctamente.')

            # Redirección para el delegado después de registrar el equipo
            if request.user.rol == 'DELEGADO':
                # Redirigir al delegado a la página de registro de pago para su equipo
                return redirect('registrar_pago_delegado')
            elif request.user.rol == 'ADMIN':
                # Redirección para el admin (si aplica, mantener la lógica existente o ajustar)
                # Assuming 'registrar_pago_para_equipo_admin' is the correct URL name for admin to register payment for an team
                return redirect('registrar_pago_para_equipo_admin', equipo_id=equipo.id)
            else:
                # Redirección por defecto si no es admin ni delegado (aunque el test_func lo impide)
                redirect_url = reverse('listar_equipos') + f'?campeonato_id={equipo.campeonato.id}'
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
    form = EquipoForm(instance=equipo)
    return render(request, 'equipo/registrar_equipo.html', {
        'form': form,
        'equipo': equipo,
        'view_mode': True  # Indica que es modo solo lectura
    })

@login_required
@user_passes_test(es_admin_o_delegado)
def editar_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo actualizado correctamente.')
            return redirect('detalle_equipo', id=equipo.id)
    else:
        form = EquipoForm(instance=equipo)
    return render(request, 'equipo/registrar_equipo.html', {
        'form': form,
        'equipo': equipo,
        'edit_mode': True  # Indica que es modo edición
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

    # Verificar si el equipo está aprobado para registrar jugadores
    if not equipo.aprobado:
        messages.error(request, "El equipo no está aprobado. No puedes registrar jugadores hasta que el pago sea aprobado.")
        return redirect('detalle_equipo', id=equipo.id) # Redirigir al detalle del equipo o a donde sea apropiado

    jugadores_data = []
    campeonato = equipo.campeonato
    for jugador in equipo.jugadores.all():
        player_stats = None
        deporte_nombre = campeonato.deporte.nombre.upper()

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

        jugadores_data.append({
            'jugador': jugador,
            'stats': player_stats,
            'deporte_nombre': deporte_nombre,
            'posicion': jugador.posicion,
        })

    return render(request, 'equipo/jugadores_equipo.html', {'equipo': equipo, 'jugadores_data': jugadores_data})

@login_required
@user_passes_test(es_admin_o_delegado)
def mis_jugadores_delegado(request):
    try:
        equipo = Equipo.objects.get(delegado=request.user)
        campeonato = equipo.campeonato
    except Equipo.DoesNotExist:
        messages.error(request, "No tienes un equipo registrado.")
        return redirect('delegado_dashboard')
    
    jugadores_data = []
    for jugador in equipo.jugadores.all():
        player_stats = None
        deporte_nombre = campeonato.deporte.nombre.upper()

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

        jugadores_data.append({
            'jugador': jugador,
            'stats': player_stats,
            'deporte_nombre': deporte_nombre,
            'posicion': jugador.posicion, # Add posicion here
        })

    return render(request, 'equipo/jugadores_equipo.html', {
        'equipo': equipo,
        'jugadores_data': jugadores_data,
        'is_delegado_view': True,
        'campeonato': campeonato, # Pass campeonato to the template
    })

@login_required
@user_passes_test(es_admin_o_delegado)
def eliminar_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    if request.method == 'POST':
        equipo.delete()
        messages.success(request, 'Equipo eliminado correctamente.')
        return redirect('listar_equipos')
    # If it's a GET request, we don't render a confirmation page anymore.
    # The confirmation is handled by the onclick in listar_equipos.html
    return redirect('listar_equipos') # Redirect back to the list after deletion attempt

