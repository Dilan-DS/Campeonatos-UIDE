from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Equipo, Campeonato
from core.forms import EquipoForm, PagoForm
from django.http import HttpResponse

def es_delegado(user):
    # Verifica si el usuario es un delegado
    return user.rol == 'DELEGADO'


@login_required
@user_passes_test(es_delegado)
# función para el dashboard del delegado
def delegado_dashboard(request):
    # Intenta obtener el equipo asociado al delegado actual
    try:
        # Utiliza select_related para optimizar la consulta y evitar consultas adicionales
        equipo = Equipo.objects.get(delegado=request.user)
        # Si el equipo tiene un campeonato, lo incluye en el contexto
    except Equipo.DoesNotExist:
        # Si no se encuentra el equipo, muestra un mensaje de error
        equipo = None

    return render(request, 'dashboard/delegado.html', {
        'equipo': equipo
    })

@user_passes_test(es_delegado)
def vista_delegado(request):
    # Esta vista es exclusiva para delegados
    return HttpResponse("Vista solo para delegado")

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


@login_required
@user_passes_test(lambda u: u.rol in ['ADMIN', 'DELEGADO'])
def ver_calendario_completo(request):
    partidos = Partido.objects.select_related('equipo_local', 'equipo_visitante', 'campeonato').order_by('fecha', 'hora')
    return render(request, 'partido/calendario_completo.html', {'partidos': partidos})
