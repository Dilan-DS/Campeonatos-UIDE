from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import ValidationError
from core.models import Equipo, Campeonato, Jugador, Usuario, Partido
from core.forms import EquipoForm, JugadorForm, PagoForm

def es_delegado(user):
    return user.rol == 'DELEGADO'

@login_required
@user_passes_test(es_delegado)
def delegado_dashboard(request):
    try:
        equipo = Equipo.objects.get(delegado=request.user)
    except Equipo.DoesNotExist:
        equipo = None
    return render(request, 'dashboard/delegado.html', {'equipo': equipo})

@login_required
@user_passes_test(es_delegado)
def registrar_equipo(request):
    campeonato_id = request.GET.get('campeonato_id')
    campeonato = get_object_or_404(Campeonato, id=campeonato_id) if campeonato_id else None

    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            equipo = form.save(commit=False)
            equipo.delegado = request.user
            equipo.campeonato = campeonato
            try:
                equipo.clean()
                equipo.save()
                messages.success(request, 'Equipo registrado correctamente.')
                return redirect('delegado_dashboard')
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = EquipoForm()

    return render(request, 'equipo/registrar_equipo.html', {'form': form, 'campeonato': campeonato})

@login_required
@user_passes_test(es_delegado)
def editar_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id, delegado=request.user)
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, instance=equipo)
        if form.is_valid():
            cleaned = form.cleaned_data
            equipo.nombre = cleaned.get('nombre', equipo.nombre)
            equipo.carrera = cleaned.get('carrera', equipo.carrera)
            if request.FILES.get('logo'):
                equipo.logo = request.FILES['logo']
            equipo.aprobado = cleaned.get('aprobado', equipo.aprobado)
            try:
                equipo.clean()
                equipo.save()
                messages.success(request, "Equipo actualizado correctamente.")
                return redirect('delegado_dashboard')
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = EquipoForm(instance=equipo)
    return render(request, 'equipo/editar_equipo.html', {'form': form, 'equipo': equipo})

@login_required
@user_passes_test(es_delegado)
def eliminar_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id, delegado=request.user)
    if request.method == 'POST':
        equipo.delete()
        messages.success(request, "Equipo eliminado correctamente.")
        return redirect('delegado_dashboard')
    return render(request, 'equipo/eliminar_equipo.html', {'equipo': equipo})

@login_required
@user_passes_test(es_delegado)
def jugadores_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id, delegado=request.user)
    jugadores = equipo.jugadores.all()
    return render(request, 'equipo/jugadores_equipo.html', {'equipo': equipo, 'jugadores': jugadores})

@login_required
@user_passes_test(es_delegado)
def registrar_jugador(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id, delegado=request.user)

    # Ajustar queryset de usuarios JUGADOR que no están asignados a ningún jugador aún
    disponibles = Usuario.objects.filter(rol='JUGADOR').exclude(jugador__isnull=False)

    if request.method == 'POST':
        form = JugadorForm(request.POST)
        # Override el campo usuario para limitar opciones a los disponibles
        form.fields['usuario'].queryset = disponibles

        if form.is_valid():
            jugador = form.save(commit=False)
            jugador.equipo = equipo
            try:
                jugador.clean()
                jugador.save()
                messages.success(request, "Jugador registrado correctamente.")
                return redirect('jugadores_equipo', equipo_id=equipo.id)
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = JugadorForm()
        form.fields['usuario'].queryset = disponibles

    return render(request, 'equipo/registrar_jugador.html', {'form': form, 'equipo': equipo})

@login_required
@user_passes_test(es_delegado)
def editar_jugador(request, pk):
    jugador = get_object_or_404(Jugador, pk=pk, equipo__delegado=request.user)

    # Usuarios disponibles para asignar: el actual + los que no tienen jugador aún
    disponibles = Usuario.objects.filter(rol='JUGADOR').exclude(jugador__isnull=False).union(
        Usuario.objects.filter(pk=jugador.usuario.pk)
    )

    if request.method == 'POST':
        form = JugadorForm(request.POST, instance=jugador)
        form.fields['usuario'].queryset = disponibles

        if form.is_valid():
            cleaned = form.cleaned_data
            # Ojo: Cambiar usuario puede ser delicado, solo si es necesario
            jugador.usuario = cleaned.get('usuario', jugador.usuario)
            jugador.numero_camiseta = cleaned.get('numero_camiseta', jugador.numero_camiseta)
            jugador.edad = cleaned.get('edad', jugador.edad)
            try:
                jugador.clean()
                jugador.save()
                messages.success(request, "Jugador actualizado correctamente.")
                return redirect('jugadores_equipo', equipo_id=jugador.equipo.id)
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = JugadorForm(instance=jugador)
        form.fields['usuario'].queryset = disponibles

    return render(request, 'equipo/editar_jugador.html', {'form': form, 'jugador': jugador})

@login_required
@user_passes_test(es_delegado)
def eliminar_jugador(request, pk):
    jugador = get_object_or_404(Jugador, pk=pk, equipo__delegado=request.user)
    equipo_id = jugador.equipo.id
    if request.method == 'POST':
        jugador.delete()
        messages.success(request, "Jugador eliminado correctamente.")
        return redirect('jugadores_equipo', equipo_id=equipo_id)
    return render(request, 'equipo/eliminar_jugador.html', {'jugador': jugador})

@login_required
@user_passes_test(es_delegado)
def pago_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id, delegado=request.user)
    pago = getattr(equipo, 'pago', None)

    if request.method == 'POST':
        form = PagoForm(request.POST, request.FILES, instance=pago)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.equipo = equipo
            pago.save()
            messages.success(request, "Pago registrado/actualizado correctamente.")
            return redirect('delegado_dashboard')
    else:
        form = PagoForm(instance=pago)

    return render(request, 'equipo/pago_equipo.html', {'form': form, 'equipo': equipo})

@login_required
@user_passes_test(es_delegado)
def ver_calendario_completo(request):
    # Solo muestra los partidos donde participa el equipo del delegado
    try:
        equipo = Equipo.objects.get(delegado=request.user)
    except Equipo.DoesNotExist:
        messages.warning(request, "No tienes un equipo asignado.")
        return redirect('delegado_dashboard')

    partidos = Partido.objects.filter(
        campeonato=equipo.campeonato
    ).filter(
        equipo_local=equipo
    ) | Partido.objects.filter(
        campeonato=equipo.campeonato,
        equipo_visitante=equipo
    )
    partidos = partidos.order_by('fecha', 'hora')

    return render(request, 'partido/calendario_equipo.html', {'partidos': partidos, 'equipo': equipo})
