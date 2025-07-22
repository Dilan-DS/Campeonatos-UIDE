from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from core.models import Equipo, Campeonato
from core.forms import EquipoForm, PagoForm

# ========================
# EQUIPOS
# ======================== 

def es_delegado(user):
    return user.rol == 'DELEGADO'

@login_required
@user_passes_test(es_delegado)
# Vista para registrar un nuevo equipo
def registrar_equipo(request):
    # Obtiene el ID del campeonato desde la solicitud GET
    campeonato_id = request.GET.get('campeonato_id')
    # Si se proporciona un ID de campeonato, intenta obtener el campeonato correspondiente
    campeonato = get_object_or_404(Campeonato, id=campeonato_id) if campeonato_id else None

    if request.method == 'POST':
        # Si la solicitud es POST, crea una instancia del formulario EquipoForm con los datos enviados
        form = EquipoForm(request.POST, request.FILES)
        # Verifica si el formulario es válido
        if form.is_valid():
            # Si el formulario es válido, crea una instancia del equipo sin guardarlo en la base de datos
            equipo = form.save(commit=False)
            # Asigna el delegado y el campeonato al equipo
            equipo.delegado = request.user
            # Si se proporciona un campeonato, lo asigna al equipo
            equipo.campeonato = campeonato
            # Guarda el equipo en la base de datos
            equipo.save()
            # Muestra un mensaje de éxito al usuario
            messages.success(request, 'Equipo registrado correctamente.')
            return redirect('vista_inicio')
    else:
        # Si la solicitud no es POST, crea un formulario vacío
        form = EquipoForm()

    return render(request, 'equipo/registrar_equipo.html', {'form': form, 'campeonato': campeonato})
# función para listar equipos
def listar_equipos(request):
    # Obtiene todos los equipos registrados en la base de datos
    equipos = list(Equipo.objects.all())
    # Ordena los equipos por puntos totales en orden descendente, manejando el caso de puntos_totales nulos
    equipos.sort(key=lambda e: e.puntos_totales or 0, reverse=True)
    # Renderiza la plantilla 'listar_equipos.html' con los equipos
    return render(request, 'equipo/listar_equipos.html', {'equipos': equipos})


def detalle_equipo(request, id):
    # Obtiene el equipo por su ID, o devuelve un error 404 si no se encuentra
    equipo = get_object_or_404(Equipo, id=id)
    # Verifica si el equipo tiene un campeonato asociado
    return render(request, 'equipo/detalle.html', {'equipo': equipo})

def editar_equipo(request, id):
    # Obtiene el equipo por su ID, o devuelve un error 404 si no se encuentra
    equipo = get_object_or_404(Equipo, id=id)
    # Verifica si la solicitud es POST (envío de formulario)
    form = EquipoForm(request.POST or None, request.FILES or None, instance=equipo)
    # Si la solicitud es POST, crea una instancia del formulario EquipoForm con los datos enviados
    if form.is_valid():
        # Verifica si el formulario es válido
        form.save()
        # Muestra un mensaje de éxito al usuario
        messages.success(request, 'Equipo actualizado correctamente.')
        # Redirige al usuario a la página de detalles del equipo
        return redirect('detalle_equipo', id=equipo.id)
    return render(request, 'equipo/editar_equipo.html', {'form': form, 'equipo': equipo})

def pago_equipo(request, id):
    # Obtiene el equipo por su ID, o devuelve un error 404 si no se encuentra
    equipo = get_object_or_404(Equipo, id=id)
    # Verifica si la solicitud es POST (envío de formulario)
    form = PagoForm(request.POST or None, request.FILES or None)
    # Si la solicitud es POST, crea una instancia del formulario PagoForm con los datos enviados
    if form.is_valid():
        # Verifica si el formulario es válido
        pago = form.save(commit=False)
        # Asigna el equipo al pago
        pago.equipo = equipo
        # Guarda el pago en la base de datos
        pago.save()
        # Muestra un mensaje de éxito al usuario
        messages.success(request, 'Pago registrado correctamente.')
        # Redirige al usuario a la página de detalles del equipo
        return redirect('detalle_equipo', id=equipo.id)
    # Si la solicitud no es POST, crea un formulario vacío
    return render(request, 'equipo/pago_equipo.html', {'form': form, 'equipo': equipo})


def jugadores_equipo(request, id):
    # Obtiene el equipo por su ID, o devuelve un error 404 si no se encuentra
    equipo = get_object_or_404(Equipo, id=id)
    # Obtiene todos los jugadores del equipo
    jugadores = equipo.jugador_set.all()
    # Renderiza la plantilla 'jugadores_equipo.html' con el equipo y los jugadores
    return render(request, 'equipo/jugadores_equipo.html', {'equipo': equipo, 'jugadores': jugadores})