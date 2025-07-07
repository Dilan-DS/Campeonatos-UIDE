from django.shortcuts import render, redirect, get_object_or_404
# Importaciones de Django
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from .models import *
from .forms import *



# ========================
# VALIDACIONES DE ROL
# ========================
#   Estas funciones se utilizan para verificar el rol del usuario autenticado.
def es_admin(user):
    return user.rol == 'ADMIN'

def es_delegado(user):
    return user.rol == 'DELEGADO'

def es_jugador(user):
    return user.rol == 'JUGADOR'

@login_required
@user_passes_test(es_admin)
def listar_codigos_qr(request):
    codigos = CodigoQR.objects.all()
    return render(request, 'codigoqr/listar.html', {'codigos': codigos})

@login_required
@user_passes_test(es_admin)
def registrar_codigo_qr(request):
    if request.method == 'POST':
        form = CodigoQRForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Código QR registrado con éxito.')
            return redirect('listar_codigos_qr')
    else:
        form = CodigoQRForm()
    return render(request, 'codigoqr/registrar.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def editar_codigo_qr(request, id):
    qr = get_object_or_404(CodigoQR, id=id)
    if request.method == 'POST':
        form = CodigoQRForm(request.POST, request.FILES, instance=qr)
        if form.is_valid():
            form.save()
            messages.success(request, 'Código QR actualizado.')
            return redirect('listar_codigos_qr')
    else:
        form = CodigoQRForm(instance=qr)
    return render(request, 'codigoqr/editar.html', {'form': form, 'codigo': qr})

@login_required
@user_passes_test(es_admin)
def eliminar_codigo_qr(request, id):
    qr = get_object_or_404(CodigoQR, id=id)
    if request.method == 'POST':
        qr.delete()
        messages.success(request, 'Código QR eliminado.')
        return redirect('listar_codigos_qr')
    return render(request, 'codigoqr/eliminar.html', {'codigo': qr})

@login_required
@user_passes_test(es_admin)
def eliminar_tipo_campeonato(request, id):
    tipo = get_object_or_404(TipoCampeonato, id=id)
    if request.method == 'POST':
        tipo.delete()
        messages.success(request, 'Tipo de campeonato eliminado correctamente.')
        return redirect('listar_tipos_campeonato')
    
    return render(request, 'tipo_campeonato/eliminar_tipo_campeonato.html', {'tipo': tipo})

@login_required
@user_passes_test(es_admin)
def editar_tipo_campeonato(request, id):
    tipo = get_object_or_404(TipoCampeonato, id=id)
    if request.method == 'POST':
        form = TipoCampeonatoForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de campeonato actualizado correctamente.')
            return redirect('listar_tipos_campeonato')
    else:
        form = TipoCampeonatoForm(instance=tipo)
    
    return render(request, 'tipo_campeonato/editar_tipo_campeonato.html', {'form': form, 'tipo': tipo})

@login_required
@user_passes_test(es_admin)
def editar_deporte(request, id):
    deporte = get_object_or_404(Deporte, id=id)
    form = DeporteForm(request.POST or None, instance=deporte)
    if form.is_valid():
        form.save()
        messages.success(request, "Deporte actualizado correctamente.")
        return redirect('listar_deportes')
    return render(request, 'deporte/editar_deporte.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def eliminar_deporte(request, id):
    deporte = get_object_or_404(Deporte, id=id)
    if request.method == 'POST':
        deporte.delete()
        messages.success(request, "Deporte eliminado correctamente.")
        return redirect('listar_deportes')
    return render(request, 'deporte/eliminar_deporte.html', {'deporte': deporte})

# ========================
# GESTIÓN DE DEPORTES Y TIPOS DE CAMPEONATO (solo admin)
# ========================

@login_required
@user_passes_test(es_admin)
def registrar_deporte(request):
    if request.method == 'POST':
        form = DeporteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_deportes')
    else:
        form = DeporteForm()
    return render(request, 'deporte/registrar.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def registrar_tipo_campeonato(request):
    if request.method == 'POST':
        form = TipoCampeonatoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_tipos_campeonato')
    else:
        form = TipoCampeonatoForm()

    return render(request, 'tipo_campeonato/registrar_tipo_campeonato.html', {'form': form})


def listar_tipos_campeonato(request):
    tipos = TipoCampeonato.objects.all()
    return render(request, 'tipo_campeonato/listar_tipos.html', {'tipos': tipos})

def listar_deportes(request):
    deportes = Deporte.objects.all()
    return render(request, 'deporte/listar_deportes.html', {'deportes': deportes})


# ========================
# DASHBOARDS POR ROL
# ========================
#   Estas vistas renderizan los dashboards específicos para cada rol de usuario.
@login_required
@user_passes_test(es_admin)
def admin_dashboard(request):
    return render(request, 'dashboard/admin.html')

@login_required
@user_passes_test(es_delegado)
def delegado_dashboard(request):
    try:
        equipo = Equipo.objects.get(delegado=request.user)
    except Equipo.DoesNotExist:
        equipo = None

    return render(request, 'dashboard/delegado.html', {
        'equipo': equipo
    })


@login_required
@user_passes_test(es_jugador)
def jugador_dashboard(request):
    try:
        jugador = Jugador.objects.select_related('equipo__campeonato').get(usuario=request.user)
        equipo = jugador.equipo
        campeonato = equipo.campeonato

        return render(request, 'dashboard/jugador.html', {
            'jugador': jugador,
            'equipo': equipo,
            'campeonato': campeonato
        })

    except Jugador.DoesNotExist:
        messages.error(request, "No se encontró tu perfil de jugador.")
        return redirect('inicio_publico')


# ========================
# AUTENTICACION
# ========================

def vista_login(request):
    if request.user.is_authenticated:
        return redirect('vista_inicio')

    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        usuario = form.get_user()
        login(request, usuario)

        # Redirige según el rol del usuario
        if usuario.rol == 'ADMIN':
            return redirect('admin_dashboard')
        elif usuario.rol == 'DELEGADO':
            return redirect('delegado_dashboard')
        elif usuario.rol == 'JUGADOR':
            return redirect('jugador_dashboard')
        else:
            return redirect('inicio_publico')

    return render(request, 'usuario/login.html', {'form': form})

def vista_registro(request):
    if request.user.is_authenticated:
        return redirect('vista_inicio')

    form = RegistroJugadorForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('jugador_dashboard')  

    return render(request, 'usuario/registro.html', {'form': form})

def vista_logout(request):
    logout(request)
    return redirect('login')

# ========================
# INICIO PÚBLICO
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
# USUARIOS POR ROL
# ========================

@user_passes_test(es_admin)
def listar_usuarios(request):
    return HttpResponse("Solo admin ve esto")

@user_passes_test(es_delegado)
def vista_delegado(request):
    return HttpResponse("Vista solo para delegado")

@user_passes_test(es_jugador)
def ver_estadisticas_jugador(request, jugador_id):
    return HttpResponse(f"Estadísticas del jugador {jugador_id}")

# ========================
# SUSPENSIONES
# ========================

def listar_suspensiones(request):
    suspensiones = Suspension.objects.select_related('jugador__usuario', 'jugador__equipo').all()
    return render(request, 'suspension/listar.html', {'suspensiones': suspensiones})

def detalle_suspension(request, suspension_id):
    suspension = get_object_or_404(Suspension, id=suspension_id)
    return render(request, 'suspension/detalle.html', {'suspension': suspension})

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

# ========================
# CAMPEONATOS PÚBLICOS
# ========================

def campeonatos_publicos(request):
    campeonatos = Campeonato.objects.filter(activo=True)
    return render(request, 'publica/lista_campeonatos.html', {'campeonatos': campeonatos})

def vista_tabla_publica(request, campeonato_id):
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)
    equipos = sorted(campeonato.equipos.all(), key=lambda e: e.puntos_totales, reverse=True)
    return render(request, 'publica/tabla_publica.html', {'campeonato': campeonato, 'equipos': equipos})

# ========================
# EQUIPOS
# ========================

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
            equipo.save()
            messages.success(request, 'Equipo registrado correctamente.')
            return redirect('vista_inicio')
    else:
        form = EquipoForm()

    return render(request, 'equipo/registrar_equipo.html', {'form': form, 'campeonato': campeonato})

def listar_equipos(request):
    equipos = list(Equipo.objects.all())
    equipos.sort(key=lambda e: e.puntos_totales or 0, reverse=True)
    return render(request, 'equipo/listar_equipos.html', {'equipos': equipos})


def detalle_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    return render(request, 'equipo/detalle.html', {'equipo': equipo})

def editar_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    form = EquipoForm(request.POST or None, request.FILES or None, instance=equipo)
    if form.is_valid():
        form.save()
        messages.success(request, 'Equipo actualizado correctamente.')
        return redirect('detalle_equipo', id=equipo.id)
    return render(request, 'equipo/editar_equipo.html', {'form': form, 'equipo': equipo})

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
# PARTIDOS
# ========================

def listar_partidos(request):
    partidos = Partido.objects.all().order_by('-fecha', '-hora')
    return render(request, 'partido/listar_partidos.html', {'partidos': partidos})

def registrar_partido(request):
    if request.method == 'POST':
        form = PartidoForm(request.POST)
        if form.is_valid():
            partido = form.save()
            messages.success(request, 'Partido registrado correctamente.')
            return redirect('listar_partidos')
    else:
        form = PartidoForm()
    return render(request, 'partido/registrar_partido.html', {'form': form})

def detalle_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    return render(request, 'partido/detalle_partido.html', {'partido': partido})

# ========================
# ESTADÍSTICAS
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
# Editar una transmisión (solo admin)
@login_required
@user_passes_test(es_admin)
def editar_transmision(request, id):
    transmision = get_object_or_404(Transmision, id=id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        url = request.POST.get('url')
        campeonato_id = request.POST.get('campeonato')

        if nombre and url and campeonato_id:
            transmision.nombre = nombre
            transmision.url = url
            transmision.campeonato = get_object_or_404(Campeonato, id=campeonato_id)
            transmision.save()
            messages.success(request, 'Transmisión actualizada correctamente.')
            return redirect('listar_transmisiones')
        else:
            messages.error(request, 'Todos los campos son obligatorios.')

    campeonatos = Campeonato.objects.all()
    return render(request, 'transmision/editar_transmision.html', {
        'transmision': transmision,
        'campeonatos': campeonatos
    })
# Eliminar una transmisión (solo admin)
@login_required
@user_passes_test(es_admin)
def eliminar_transmision(request, id):
    transmision = get_object_or_404(Transmision, id=id)

    if request.method == 'POST':
        transmision.delete()
        messages.success(request, 'Transmisión eliminada correctamente.')
        return redirect('listar_transmisiones')

    return render(request, 'transmision/eliminar_transmision.html', {
        'transmision': transmision
    })

@login_required
@user_passes_test(es_admin)
def crear_usuario_admin(request):
    if request.method == 'POST':
        form = CrearUsuarioAdminForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('admin_dashboard')
    else:
        form = CrearUsuarioAdminForm()
    return render(request, 'admin_panel/registro_usuario.html', {'form': form})
