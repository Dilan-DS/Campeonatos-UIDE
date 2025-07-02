from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Campeonato, Equipo, Arbitro, Transmision
from .forms import ArbitroForm, CampeonatoForm, PagoForm, EquipoForm, TransmisionForm  
from django.contrib import messages


def vista_registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # después de registrarse va al login
    
    return render(request, 'usuario/registro.html', {'form': form})


def vista_inicio(request):
    equipos = list(Equipo.objects.all())
    equipos.sort(key=lambda e: e.puntos_totales, reverse=True)  # ordena por puntos_totales
    return render(request, 'inicio/inicio.html', {'equipos': equipos})


def vista_login(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('inicio')
    return render(request, 'usuario/login.html', {'form': form})


def vista_logout(request):
    logout(request)
    return redirect('login')


def detalle_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    return render(request, 'equipo/detalle.html', {'equipo': equipo})


def vista_inicio_publico(request):
    equipos = list(Equipo.objects.all())
    equipos.sort(key=lambda e: e.puntos_totales, reverse=True)  # igual que en vista_inicio
    return render(request, 'inicio/inicio_publico.html', {'equipos': equipos})

def vista_dashboard(request):
    total_campeonatos = Campeonato.objects.count()
    total_equipos = Equipo.objects.count()
    total_arbitros = Arbitro.objects.count()
    return render(request, 'admin_panel/dashboard.html', {
        'total_campeonatos': total_campeonatos,
        'total_equipos': total_equipos,
        'total_arbitros': total_arbitros,
    })

def detalle_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    return render(request, 'equipo/detalle.html', {'equipo': equipo})

def listar_equipos(request):
    equipos = Equipo.objects.all().order_by('-puntos_totales')
    return render(request, 'equipo/listar_equipos.html', {'equipos': equipos})

def registrar_equipo(request):
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo registrado correctamente.')
            return redirect('listar_equipos')
    else:
        form = EquipoForm()
    return render(request, 'equipo/registrar_equipo.html', {'form': form})

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
    return render(request, 'equipo/editar_equipo.html', {'form': form, 'equipo': equipo})

def pago_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    if request.method == 'POST':
        form = PagoForm(request.POST, request.FILES)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.equipo = equipo
            pago.save()
            messages.success(request, 'Pago registrado correctamente.')
            return redirect('detalle_equipo', id=equipo.id)
    else:
        form = PagoForm()
    return render(request, 'equipo/pago_equipo.html', {'form': form, 'equipo': equipo})

def jugadores_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    jugadores = equipo.jugador_set.all()
    return render(request, 'equipo/jugadores_equipo.html', {'equipo': equipo, 'jugadores': jugadores})


# Vistas de Árbitros
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


# Vistas de Campeonatos
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

def estadisticas_ajedrez(request):
    return render(request, 'estadisticas/estadisticas_ajedrez.html')

def estadisticas_basquet(request):
    return render(request, 'estadisticas/estadisticas_basquet.html')

def estadisticas_ecuaboly(request):
    return render(request, 'estadisticas/estadisticas_ecuaboly.html')

def estadisticas_futbol(request):
    return render(request, 'estadisticas/estadisticas_futbol.html')

def estadisticas_futbolin(request):
    return render(request, 'estadisticas/estadisticas_futbolin.html')

def estadisticas_pingpong(request):
    return render(request, 'estadisticas/estadisticas_pingpong.html')

def estadisticas_tenis(request):
    return render(request, 'estadisticas/estadisticas_tenis.html')

def estadisticas_videojuegos(request):
    return render(request, 'estadisticas/estadisticas_videojuegos.html')

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
    else:
        campeonatos = Campeonato.objects.all()
        return render(request, 'transmision/registrar_transmision.html', {'campeonatos': campeonatos})


def detalle_transmision(request, id):
    transmision = get_object_or_404(Transmision, id=id)
    return render(request, 'transmision/detalle_transmision.html', {'transmision': transmision})