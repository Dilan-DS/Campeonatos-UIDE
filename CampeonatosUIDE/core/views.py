from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import date
from django.http import HttpResponse
from .models import Partido
from .forms import PartidoForm
from .models import Suspension
from .forms import SuspensionForm

def es_admin(user):
    return user.rol == 'ADMIN'

def es_delegado(user):
    return user.rol == 'DELEGADO'

def es_jugador(user):
    return user.rol == 'JUGADOR'


@user_passes_test(es_admin)
def listar_usuarios(request):
    # solo el admin ve esto
    pass

@user_passes_test(es_delegado)
def registrar_equipo(request):
    # solo delegado puede crear
    pass

@user_passes_test(es_jugador)
def ver_estadisticas_jugador(request, jugador_id):
    # solo jugadores
    pass

# Listar suspensiones
def listar_suspensiones(request):
    suspensiones = Suspension.objects.select_related('jugador__usuario', 'jugador__equipo').all()
    return render(request, 'suspension/listar.html', {'suspensiones': suspensiones})

# Detalle de una suspensión
def detalle_suspension(request, suspension_id):
    suspension = get_object_or_404(Suspension, id=suspension_id)
    return render(request, 'suspension/detalle.html', {'suspension': suspension})

# Registrar nueva suspensión
def registrar_suspension(request):
    if request.method == 'POST':
        form = SuspensionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Suspensión registrada correctamente.")
            return redirect('listar_suspensiones')
    else:
        form = SuspensionForm()
    return render(request, 'suspension/registrar.html', {'form': form})

# Modelos
from .models import Campeonato, Equipo, Arbitro, Transmision

# Formularios
from .forms import (
    ArbitroForm, CampeonatoForm, PagoForm,
    EquipoForm, TransmisionForm, CustomUsuarioCreationForm
)

def listar_partidos(request):
    partidos = Partido.objects.all().order_by('-fecha', '-hora')
    return render(request, 'partido/listar_partidos.html', {'partidos': partidos})

def registrar_partido(request):
    if request.method == 'POST':
        form = PartidoForm(request.POST)
        if form.is_valid():
            partido = form.save()
            messages.success(request, ' Partido registrado correctamente.')
            return redirect('listar_partidos')
    else:
        form = PartidoForm()
    return render(request, 'partido/registrar_partido.html', {'form': form})

def detalle_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    return render(request, 'partido/detalle_partido.html', {'partido': partido})
# ========================
# AUTENTICACION
# ========================

def vista_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, 'usuario/login.html', {'form': form})
def vista_registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    form = CustomUsuarioCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    
    return render(request, 'usuario/registro.html', {'form': form})


def vista_logout(request):
    logout(request)
    return redirect('login')

# ========================
# INICIO PÚBLICO Y PRIVADO
# ========================

def vista_inicio_publico(request):
    return render(request, 'publica/inicio_publico.html')

def vista_inicio(request):
    return render(request, 'publica/inicio_publico.html')

# ========================
# PERFIL DE USUARIO
# ========================

@login_required
def vista_perfil_usuario(request):
    return render(request, 'usuario/perfil.html')

@login_required
def editar_perfil(request):
    return render(request, 'usuario/editar_perfil.html')

# ========================
# CAMPEONATOS PÚBLICOS
# ========================

def campeonatos_publicos(request):
    campeonatos = Campeonato.objects.filter(estado='activo')
    return render(request, 'publica/lista_campeonatos.html', {'campeonatos': campeonatos})

def vista_tabla_publica(request, campeonato_id):
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)
    equipos = sorted(campeonato.equipos.all(), key=lambda e: e.puntos_totales, reverse=True)
    return render(request, 'publica/tabla_publica.html', {'campeonato': campeonato, 'equipos': equipos})

# ========================
# EQUIPOS
# ========================

def listar_equipos(request):
    equipos = Equipo.objects.all().order_by('-puntos_totales')
    return render(request, 'equipo/listar_equipos.html', {'equipos': equipos})

def registrar_equipo(request):
    campeonato_id = request.GET.get('campeonato_id')
    campeonato = get_object_or_404(Campeonato, id=campeonato_id) if campeonato_id else None

    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            equipo = form.save(commit=False)
            equipo.fk_delegado = request.user
            equipo.campeonato = campeonato
            equipo.save()
            messages.success(request, 'Equipo registrado correctamente.')
            return redirect('inicio_publico')
    else:
        form = EquipoForm()

    return render(request, 'equipo/registrar_equipo.html', {'form': form, 'campeonato': campeonato})

def editar_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    form = EquipoForm(request.POST or None, request.FILES or None, instance=equipo)
    if form.is_valid():
        form.save()
        messages.success(request, 'Equipo actualizado correctamente.')
        return redirect('detalle_equipo', id=equipo.id)
    return render(request, 'equipo/editar_equipo.html', {'form': form, 'equipo': equipo})

def detalle_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    return render(request, 'equipo/detalle.html', {'equipo': equipo})

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

def jugadores_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    jugadores = equipo.jugador_set.all()
    return render(request, 'equipo/jugadores_equipo.html', {'equipo': equipo, 'jugadores': jugadores})

# ========================
# ARBITROS
# ========================

def listar_arbitros(request):
    arbitros = Arbitro.objects.all()
    return render(request, 'arbitro/listar.html', {'arbitros': arbitros})

def registrar_arbitro(request):
    form = ArbitroForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('listar_arbitros')
    return render(request, 'arbitro/registrar.html', {'form': form})

def editar_arbitro(request, id):
    arbitro = get_object_or_404(Arbitro, id=id)
    form = ArbitroForm(request.POST or None, instance=arbitro)
    if form.is_valid():
        form.save()
        return redirect('listar_arbitros')
    return render(request, 'arbitro/editar.html', {'form': form, 'arbitro': arbitro})

def detalle_arbitro(request, id):
    arbitro = get_object_or_404(Arbitro, id=id)
    return render(request, 'arbitro/detalle.html', {'arbitro': arbitro})

# ========================
# CAMPEONATOS PRIVADOS
# ========================

def listar_campeonatos(request):
    campeonatos = Campeonato.objects.all()
    return render(request, 'campeonato/listar.html', {'campeonatos': campeonatos})

def crear_campeonato(request):
    form = CampeonatoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('listar_campeonatos')
    return render(request, 'campeonato/crear.html', {'form': form})

def editar_campeonato(request, id):
    campeonato = get_object_or_404(Campeonato, id=id)
    form = CampeonatoForm(request.POST or None, request.FILES or None, instance=campeonato)
    if form.is_valid():
        form.save()
        return redirect('listar_campeonatos')
    return render(request, 'campeonato/editar.html', {'form': form, 'campeonato': campeonato})

def detalle_campeonato(request, id):
    campeonato = get_object_or_404(Campeonato, id=id)
    return render(request, 'campeonato/detalle.html', {'campeonato': campeonato})

def fixture_campeonato(request, id):
    campeonato = get_object_or_404(Campeonato, id=id)
    return render(request, 'campeonato/fixture.html', {'campeonato': campeonato})

# ========================
# ESTADISTICAS
# ========================

def estadisticas_futbol(request):
    return render(request, 'estadisticas/estadisticas_futbol.html')

def estadisticas_basquet(request):
    return render(request, 'estadisticas/estadisticas_basquet.html')

def estadisticas_ecuaboly(request):
    return render(request, 'estadisticas/estadisticas_ecuaboly.html')

def estadisticas_ajedrez(request):
    return render(request, 'estadisticas/estadisticas_ajedrez.html')

def estadisticas_futbolin(request):
    return render(request, 'estadisticas/estadisticas_futbolin.html')

def estadisticas_pingpong(request):
    return render(request, 'estadisticas/estadisticas_pingpong.html')

def estadisticas_tenis(request):
    return render(request, 'estadisticas/estadisticas_tenis.html')

def estadisticas_videojuegos(request):
    return render(request, 'estadisticas/estadisticas_videojuegos.html')

# ========================
# TRANSMISIONES
# ========================

def listar_transmisiones(request):
    transmisiones = Transmision.objects.all()
    return render(request, 'transmision/listar_transmisiones.html', {'transmisiones': transmisiones})

def registrar_transmision(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        url = request.POST.get('url')
        campeonato_id = request.POST.get('campeonato')
        campeonato = get_object_or_404(Campeonato, id=campeonato_id)
        Transmision.objects.create(nombre=nombre, url=url, campeonato=campeonato)
        return redirect('listar_transmisiones')
    campeonatos = Campeonato.objects.all()
    return render(request, 'transmision/registrar_transmision.html', {'campeonatos': campeonatos})

def detalle_transmision(request, id):
    transmision = get_object_or_404(Transmision, id=id)
    return render(request, 'transmision/detalle_transmision.html', {'transmision': transmision})
