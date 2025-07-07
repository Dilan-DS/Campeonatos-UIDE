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
    # Verifica si el usuario es un administrador
    return user.rol == 'ADMIN'

def es_delegado(user):
    # Verifica si el usuario es un delegado
    return user.rol == 'DELEGADO'

def es_jugador(user):
    # Verifica si el usuario es un jugador
    return user.rol == 'JUGADOR'
# dar
@login_required
@user_passes_test(es_admin)
# funcion para listar códigos QR
def listar_codigos_qr(request):
    # Obtiene todos los códigos QR registrados en la base de datos
    codigos = CodigoQR.objects.all()
    # Renderiza la plantilla 'listar.html' con los códigos QR
    return render(request, 'codigoqr/listar.html', {'codigos': codigos})

@login_required
@user_passes_test(es_admin)
# funcion para registrar un nuevo código QR
def registrar_codigo_qr(request):
    # Verifica si la solicitud es POST (envío de formulario)
    if request.method == 'POST':
        # Crea una instancia del formulario CodigoQRForm con los datos enviados
        form = CodigoQRForm(request.POST, request.FILES)
        # Verifica si el formulario es válido
        if form.is_valid():
            # Guarda el formulario, lo que crea un nuevo objeto CodigoQR en la base de datos
            form.save()
            # Muestra un mensaje de éxito al usuario
            messages.success(request, 'Código QR registrado con éxito.')
            # Redirige al usuario a la lista de códigos QR
            return redirect('listar_codigos_qr')
    else:
        # Si la solicitud no es POST, crea un formulario vacío
        form = CodigoQRForm()
    # Renderiza la plantilla 'registrar.html' con el formulario
    return render(request, 'codigoqr/registrar.html', {'form': form})

@login_required
@user_passes_test(es_admin)
# funcion para editar un código QR existente
def editar_codigo_qr(request, id):
    # Obtiene el código QR por su ID, o devuelve un error 404 si no se encuentra
    qr = get_object_or_404(CodigoQR, id=id)
    # Verifica si la solicitud es POST (envío de formulario)
    if request.method == 'POST':
        # Crea una instancia del formulario CodigoQRForm con los datos enviados y la instancia del código QR
        form = CodigoQRForm(request.POST, request.FILES, instance=qr)
        # Verifica si el formulario es válido
        if form.is_valid():
            # Guarda el formulario, lo que actualiza el objeto CodigoQR en la base de datos
            form.save()
            # Muestra un mensaje de éxito al usuario
            messages.success(request, 'Código QR actualizado.')
            # Redirige al usuario a la lista de códigos QR
            return redirect('listar_codigos_qr')
    else:
        # Si la solicitud no es POST, crea un formulario con los datos del código QR existente
        form = CodigoQRForm(instance=qr)
    # Renderiza la plantilla 'editar.html' con el formulario y el código QR
    return render(request, 'codigoqr/editar.html', {'form': form, 'codigo': qr})

@login_required
@user_passes_test(es_admin)
# funcion para eliminar un código QR
def eliminar_codigo_qr(request, id):
    # Obtiene el código QR por su ID, o devuelve un error 404 si no se encuentra
    qr = get_object_or_404(CodigoQR, id=id)
    # Verifica si la solicitud es POST (confirmación de eliminación)
    if request.method == 'POST':
        # Elimina el código QR de la base de datos
        qr.delete()
        # Muestra un mensaje de éxito al usuario
        messages.success(request, 'Código QR eliminado.')
        # Redirige al usuario a la lista de códigos QR
        return redirect('listar_codigos_qr')
    # Si la solicitud no es POST, renderiza la plantilla de confirmación de eliminación
    return render(request, 'codigoqr/eliminar.html', {'codigo': qr})

@login_required
@user_passes_test(es_admin)
# función para eliminar un tipo de campeonato
def eliminar_tipo_campeonato(request, id):
    # Obtiene el tipo de campeonato por su ID, o devuelve un error 404 si no se encuentra
    tipo = get_object_or_404(TipoCampeonato, id=id)
    # Verifica si la solicitud es POST (confirmación de eliminación)
    if request.method == 'POST':
        # Elimina el tipo de campeonato de la base de datos
        tipo.delete()
        # Muestra un mensaje de éxito al usuario
        messages.success(request, 'Tipo de campeonato eliminado correctamente.')
        # Redirige al usuario a la lista de tipos de campeonato
        return redirect('listar_tipos_campeonato')
    # Si la solicitud no es POST, renderiza la plantilla de confirmación de eliminación
    return render(request, 'tipo_campeonato/eliminar_tipo_campeonato.html', {'tipo': tipo})

@login_required
@user_passes_test(es_admin)
# función para editar un tipo de campeonato
def editar_tipo_campeonato(request, id):
    # Obtiene el tipo de campeonato por su ID, o devuelve un error 404 si no se encuentra
    tipo = get_object_or_404(TipoCampeonato, id=id)
    # Verifica si la solicitud es POST (envío de formulario)
    if request.method == 'POST':
        # Crea una instancia del formulario TipoCampeonatoForm con los datos enviados y la instancia del tipo
        form = TipoCampeonatoForm(request.POST, instance=tipo)
        # Verifica si el formulario es válido
        if form.is_valid():
            # Guarda el formulario, lo que actualiza el objeto TipoCampeonato en la base de datos
            form.save()
            # Muestra un mensaje de éxito al usuario
            messages.success(request, 'Tipo de campeonato actualizado correctamente.')
            # Redirige al usuario a la lista de tipos de campeonato
            return redirect('listar_tipos_campeonato')
    else:
        # Si la solicitud no es POST, crea un formulario con los datos del tipo de campeonato existente
        form = TipoCampeonatoForm(instance=tipo)
    # Renderiza la plantilla 'editar_tipo_campeonato.html' con el formulario y el tipo de campeonato
    return render(request, 'tipo_campeonato/editar_tipo_campeonato.html', {'form': form, 'tipo': tipo})

@login_required
@user_passes_test(es_admin)
# función para editar deportes
def editar_deporte(request, id):
    # Obtiene el deporte por su ID, o devuelve un error 404 si no se encuentra
    deporte = get_object_or_404(Deporte, id=id)
    # Verifica si la solicitud es POST (envío de formulario)
    form = DeporteForm(request.POST or None, instance=deporte)
    # Si la solicitud es POST, crea una instancia del formulario DeporteForm con los datos enviados
    if form.is_valid():
        # Verifica si el formulario es válido
        form.save()
        # Muestra un mensaje de éxito al usuario
        messages.success(request, "Deporte actualizado correctamente.")
        # Redirige al usuario a la lista de deportes
        return redirect('listar_deportes')
    # Si la solicitud no es POST, crea un formulario con los datos del deporte existente
    return render(request, 'deporte/editar_deporte.html', {'form': form})

@login_required
@user_passes_test(es_admin)
# función para eliminar un deporte
def eliminar_deporte(request, id):
    # Obtiene el deporte por su ID, o devuelve un error 404 si no se encuentra
    deporte = get_object_or_404(Deporte, id=id)
    # Verifica si la solicitud es POST (confirmación de eliminación)
    if request.method == 'POST':
        # Elimina el deporte de la base de datos
        deporte.delete()
        # Muestra un mensaje de éxito al usuario
        messages.success(request, "Deporte eliminado correctamente.")
        # Redirige al usuario a la lista de deportes
        return redirect('listar_deportes')
    return render(request, 'deporte/eliminar_deporte.html', {'deporte': deporte})

# ========================
# GESTIÓN DE DEPORTES Y TIPOS DE CAMPEONATO (solo admin)
# ========================

@login_required
@user_passes_test(es_admin)
# función para registrar un nuevo deporte
def registrar_deporte(request):
    # Verifica si la solicitud es POST (envío de formulario)
    if request.method == 'POST':
        # Crea una instancia del formulario DeporteForm con los datos enviados
        form = DeporteForm(request.POST)
        # Verifica si el formulario es válido
        if form.is_valid():
            # Guarda el formulario, lo que crea un nuevo objeto Deporte en la base de datos
            form.save()
            # Muestra un mensaje de éxito al usuario
            return redirect('listar_deportes')

    else:
        # Si la solicitud no es POST, crea un formulario vacío
        form = DeporteForm()
    # Renderiza la plantilla 'registrar.html' con el formulario
    return render(request, 'deporte/registrar.html', {'form': form})

@login_required
@user_passes_test(es_admin)
# función para registrar un nuevo tipo de campeonato
def registrar_tipo_campeonato(request):
    # Verifica si la solicitud es POST (envío de formulario)
    if request.method == 'POST':
        # Crea una instancia del formulario TipoCampeonatoForm con los datos enviados
        form = TipoCampeonatoForm(request.POST)
        # Verifica si el formulario es válido
        if form.is_valid():
            # Guarda el formulario, lo que crea un nuevo objeto TipoCampeonato en la base de datos
            form.save()
       
            return redirect('listar_tipos_campeonato')  
    else:
        form = TipoCampeonatoForm()

    return render(request, 'tipo_campeonato/registrar_tipo_campeonato.html', {'form': form})

# funcion de listar tipos de campeonato
def listar_tipos_campeonato(request):
    # Obtiene todos los tipos de campeonato registrados en la base de datos
    tipos = TipoCampeonato.objects.all()
    # Renderiza la plantilla 'listar_tipos.html' con los tipos de campeonato
    return render(request, 'tipo_campeonato/listar_tipos.html', {'tipos': tipos})

def listar_deportes(request):
    # Obtiene todos los deportes registrados en la base de datos

    deportes = Deporte.objects.all()
    # Renderiza la plantilla 'listar_deportes.html' con los deportes
    return render(request, 'deporte/listar_deportes.html', {'deportes': deportes})


# ========================
# DASHBOARDS POR ROL
# ========================
#   Estas vistas renderizan los dashboards específicos para cada rol de usuario.
@login_required
@user_passes_test(es_admin)
# función para el dashboard del administrador
def admin_dashboard(request):
    # Renderiza la plantilla 'admin.html' para el dashboard del administrador
    return render(request, 'dashboard/admin.html')

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


@login_required
@user_passes_test(es_jugador)
# función para el dashboard del jugador
def jugador_dashboard(request):
    # Intenta obtener el jugador asociado al usuario actual
    try:
        # Utiliza select_related para optimizar la consulta y evitar consultas adicionales
        jugador = Jugador.objects.select_related('equipo__campeonato').get(usuario=request.user)
        # Si el jugador tiene un equipo y un campeonato, los incluye en el contexto
        equipo = jugador.equipo
        # Si el equipo tiene un campeonato, lo incluye en el contexto
        campeonato = equipo.campeonato
        # Renderiza la plantilla 'jugador.html' con el jugador, equipo y campeonato
        return render(request, 'dashboard/jugador.html', {
            'jugador': jugador,
            'equipo': equipo,
            'campeonato': campeonato
        })
    # Si no se encuentra el jugador, muestra un mensaje de error y redirige al inicio público
    except Jugador.DoesNotExist:
        messages.error(request, "No se encontró tu perfil de jugador.")
        return redirect('inicio_publico')


# ========================
# AUTENTICACION
# ========================

def vista_login(request):
    # Si el usuario ya está autenticado, redirige al dashboard correspondiente
    if request.user.is_authenticated:
        # Redirige al dashboard del administrador si es admin
        return redirect('vista_inicio')
    # Crea una instancia del formulario de autenticación
    form = AuthenticationForm(request, data=request.POST or None)
    # Si el formulario es válido, autentica al usuario
    if form.is_valid():
        # Autentica al usuario con el nombre de usuario y contraseña proporcionados
        usuario = form.get_user()
        # Inicia sesión para el usuario autenticado
        login(request, usuario)

        # Redirige según el rol del usuario
        if usuario.rol == 'ADMIN':
            # Redirige al dashboard del administrador
            return redirect('admin_dashboard')
        elif usuario.rol == 'DELEGADO':
            # Redirige al dashboard del delegado
            return redirect('delegado_dashboard')
        elif usuario.rol == 'JUGADOR':
            # Redirige al dashboard del jugador
            return redirect('jugador_dashboard')
        else:
            # Si el rol no es reconocido, redirige al inicio público
            return redirect('inicio_publico')

    return render(request, 'usuario/login.html', {'form': form})
# Función para registrar un nuevo jugador
def vista_registro(request):
    # Si el usuario ya está autenticado, redirige al dashboard correspondiente
    if request.user.is_authenticated:
        # Redirige al dashboard del jugador si es un jugador
        return redirect('vista_inicio')
    # Crea una instancia del formulario de registro de jugador
    form = RegistroJugadorForm(request.POST or None)
    # Si el formulario es válido, guarda el nuevo usuario y lo autentica
    if form.is_valid():
        # Guarda el formulario, lo que crea un nuevo usuario
        user = form.save()
        # Asigna el rol de 'JUGADOR' al nuevo usuario
        login(request, user)
        # Redirige al dashboard del jugador después de registrarse
        return redirect('jugador_dashboard')  

    return render(request, 'usuario/registro.html', {'form': form})
# Función para cerrar sesión
def vista_logout(request):
    # Cierra la sesión del usuario actual
    logout(request)
    # Muestra un mensaje de éxito al usuario
    return redirect('login')

# ========================
# INICIO PÚBLICO
# ========================
# Esta vista renderiza la página de inicio pública del sitio.
def vista_inicio_publico(request):
    # Si el usuario ya está autenticado, redirige al dashboard correspondiente
    return render(request, 'publica/inicio_publico.html')
# Esta vista renderiza la página de inicio pública del sitio.
def vista_inicio(request):
    # Si el usuario ya está autenticado, redirige al dashboard correspondiente
    return render(request, 'publica/inicio_publico.html')

# ========================
# PERFIL DE USUARIO
# ========================
## Esta vista renderiza el perfil del usuario autenticado.
@login_required
def vista_perfil_usuario(request):
    # Obtiene el usuario autenticado
    return render(request, 'usuario/perfil.html')

@login_required
def editar_perfil(request):
    # Obtiene el usuario autenticado
    return render(request, 'usuario/editar_perfil.html')

# ========================
# USUARIOS POR ROL
# ========================

@user_passes_test(es_admin)
# Vista para el dashboard del administrador
def listar_usuarios(request):
    # Obtiene todos los usuarios registrados en la base de datos
    return HttpResponse("Solo admin ve esto")

@user_passes_test(es_delegado)
def vista_delegado(request):
    # Esta vista es exclusiva para delegados
    return HttpResponse("Vista solo para delegado")

@user_passes_test(es_jugador)
def ver_estadisticas_jugador(request, jugador_id):
    # Esta vista es exclusiva para jugadores
    return HttpResponse(f"Estadísticas del jugador {jugador_id}")

# ========================
# SUSPENSIONES
# ========================

def listar_suspensiones(request):
    # Obtiene todas las suspensiones registradas en la base de datos
    suspensiones = Suspension.objects.select_related('jugador__usuario', 'jugador__equipo').all()
    # Ordena las suspensiones por fecha de inicio en orden descendente
    return render(request, 'suspension/listar.html', {'suspensiones': suspensiones})

def detalle_suspension(request, suspension_id):
    # Obtiene la suspensión por su ID, o devuelve un error 404 si no se encuentra
    suspension = get_object_or_404(Suspension, id=suspension_id)
    # Renderiza la plantilla 'detalle.html' con la suspensión
    return render(request, 'suspension/detalle.html', {'suspension': suspension})

def registrar_suspension(request):
    # Verifica si la solicitud es POST (envío de formulario)
    if request.method == 'POST':
        # Crea una instancia del formulario SuspensionForm con los datos enviados
        form = SuspensionForm(request.POST)
        # Verifica si el formulario es válido
        if form.is_valid():
            # Guarda el formulario, lo que crea un nuevo objeto Suspension en la base de datos
            form.save()
            # Muestra un mensaje de éxito al usuario
            messages.success(request, "Suspensión registrada correctamente.")
            # Redirige al usuario a la lista de suspensiones
            return redirect('listar_suspensiones')
    else:
        form = SuspensionForm()
    return render(request, 'suspension/registrar.html', {'form': form})

# ========================
# CAMPEONATOS PÚBLICOS
# ========================

def campeonatos_publicos(request):
    # Obtiene todos los campeonatos activos (públicos) de la base de datos
    campeonatos = Campeonato.objects.filter(activo=True)
    # Ordena los campeonatos por fecha de inicio en orden descendente
    return render(request, 'publica/lista_campeonatos.html', {'campeonatos': campeonatos})

def vista_tabla_publica(request, campeonato_id):
    # Obtiene el campeonato por su ID, o devuelve un error 404 si no se encuentra
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)
    # Obtiene todos los equipos del campeonato y los ordena por puntos totales en orden descendente
    equipos = sorted(campeonato.equipos.all(), key=lambda e: e.puntos_totales, reverse=True)
    # Renderiza la plantilla 'tabla_publica.html' con el campeonato y los equipos
    return render(request, 'publica/tabla_publica.html', {'campeonato': campeonato, 'equipos': equipos})

# ========================
# EQUIPOS
# ========================

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

# ========================
# ARBITROS
# ========================

def listar_arbitros(request):
    # Obtiene todos los árbitros registrados en la base de datos
    arbitros = Arbitro.objects.all()
    # Renderiza la plantilla 'listar.html' con los árbitros
    return render(request, 'arbitro/listar.html', {'arbitros': arbitros})

def registrar_arbitro(request):
    # Verifica si la solicitud es POST (envío de formulario)
    form = ArbitroForm(request.POST or None)
    # Si la solicitud es POST, crea una instancia del formulario ArbitroForm con los datos enviados
    if form.is_valid():
        # Verifica si el formulario es válido
        form.save()
        # Muestra un mensaje de éxito al usuario
        return redirect('listar_arbitros')
    # Si la solicitud no es POST, crea un formulario vacío
    return render(request, 'arbitro/registrar.html', {'form': form})

def editar_arbitro(request, id):
    # Obtiene el árbitro por su ID, o devuelve un error 404 si no se encuentra
    arbitro = get_object_or_404(Arbitro, id=id)
    # Verifica si la solicitud es POST (envío de formulario)
    form = ArbitroForm(request.POST or None, instance=arbitro)
    # Si la solicitud es POST, crea una instancia del formulario ArbitroForm con los datos enviados
    if form.is_valid():
        # Verifica si el formulario es válido
        form.save()
        # Muestra un mensaje de éxito al usuario
        return redirect('listar_arbitros')
    return render(request, 'arbitro/editar.html', {'form': form, 'arbitro': arbitro})

def detalle_arbitro(request, id):
    # Obtiene el árbitro por su ID, o devuelve un error 404 si no se encuentra
    arbitro = get_object_or_404(Arbitro, id=id)
    # Renderiza la plantilla 'detalle.html' con el árbitro
    return render(request, 'arbitro/detalle.html', {'arbitro': arbitro})

# ========================
# CAMPEONATOS PRIVADOS
# ========================

def listar_campeonatos(request):
    # Obtiene todos los campeonatos registrados en la base de datos
    campeonatos = Campeonato.objects.all()
    # Ordena los campeonatos por fecha de inicio en orden descendente
    return render(request, 'campeonato/listar.html', {'campeonatos': campeonatos})

def crear_campeonato(request):
    # Verifica si la solicitud es POST (envío de formulario)
    form = CampeonatoForm(request.POST or None, request.FILES or None)
    # Si la solicitud es POST, crea una instancia del formulario CampeonatoForm con los datos enviados
    if form.is_valid():
        # Verifica si el formulario es válido
        form.save()
        # Muestra un mensaje de éxito al usuario
        return redirect('listar_campeonatos')
    return render(request, 'campeonato/crear.html', {'form': form})

def editar_campeonato(request, id):
    # Obtiene el campeonato por su ID, o devuelve un error 404 si no se encuentra
    campeonato = get_object_or_404(Campeonato, id=id)
    # Verifica si la solicitud es POST (envío de formulario)
    form = CampeonatoForm(request.POST or None, request.FILES or None, instance=campeonato)
    # Si la solicitud es POST, crea una instancia del formulario CampeonatoForm con los datos enviados
    if form.is_valid():
        # Verifica si el formulario es válido
        form.save()
        # Muestra un mensaje de éxito al usuario
        return redirect('listar_campeonatos')
    return render(request, 'campeonato/editar.html', {'form': form, 'campeonato': campeonato})

def detalle_campeonato(request, id):
    # Obtiene el campeonato por su ID, o devuelve un error 404 si no se encuentra
    campeonato = get_object_or_404(Campeonato, id=id)
    # Verifica si el campeonato tiene un tipo asociado
    return render(request, 'campeonato/detalle.html', {'campeonato': campeonato})

def fixture_campeonato(request, id):
    # Obtiene el campeonato por su ID, o devuelve un error 404 si no se encuentra
    campeonato = get_object_or_404(Campeonato, id=id)
    # Obtiene todos los partidos del campeonato y los ordena por fecha y hora
    return render(request, 'campeonato/fixture.html', {'campeonato': campeonato})

# ========================
# PARTIDOS
# ========================

def listar_partidos(request):
    # Obtiene todos los partidos registrados en la base de datos y los ordena por fecha y hora
    partidos = Partido.objects.all().order_by('-fecha', '-hora')
    # Renderiza la plantilla 'listar_partidos.html' con los partidos
    return render(request, 'partido/listar_partidos.html', {'partidos': partidos})

def registrar_partido(request):
    # Verifica si la solicitud es POST (envío de formulario)
    if request.method == 'POST':
        # Crea una instancia del formulario PartidoForm con los datos enviados
        form = PartidoForm(request.POST)
        # Verifica si el formulario es válido
        if form.is_valid():
            # Si el formulario es válido, guarda el nuevo partido en la base de datos
            partido = form.save()
            # Muestra un mensaje de éxito al usuario
            messages.success(request, 'Partido registrado correctamente.')
            # Redirige al usuario a la lista de partidos
            return redirect('listar_partidos')
    else:
        # Si la solicitud no es POST, crea un formulario vacío
        form = PartidoForm()
    # Renderiza la plantilla 'registrar_partido.html' con el formulario
    return render(request, 'partido/registrar_partido.html', {'form': form})

def detalle_partido(request, partido_id):
    # Obtiene el partido por su ID, o devuelve un error 404 si no se encuentra
    partido = get_object_or_404(Partido, id=partido_id)
    # Verifica si el partido tiene un campeonato asociado
    return render(request, 'partido/detalle_partido.html', {'partido': partido})

# ========================
# ESTADÍSTICAS
# ========================

def estadisticas_futbol(request):
    # Renderiza la plantilla 'estadisticas_futbol.html' para mostrar las estadísticas de fútbol
    return render(request, 'estadisticas/estadisticas_futbol.html')

def estadisticas_basquet(request):
    # Renderiza la plantilla 'estadisticas_basquet.html' para mostrar las estadísticas de baloncesto
    return render(request, 'estadisticas/estadisticas_basquet.html')

def estadisticas_ecuaboly(request):
    # Renderiza la plantilla 'estadisticas_ecuaboly.html' para mostrar las estadísticas de Ecuaboly
    return render(request, 'estadisticas/estadisticas_ecuaboly.html')

def estadisticas_ajedrez(request):
    # Renderiza la plantilla 'estadisticas_ajedrez.html' para mostrar las estadísticas de ajedrez
    return render(request, 'estadisticas/estadisticas_ajedrez.html')

def estadisticas_futbolin(request):
    # Renderiza la plantilla 'estadisticas_futbolin.html' para mostrar las estadísticas de futbolín
    return render(request, 'estadisticas/estadisticas_futbolin.html')

def estadisticas_pingpong(request):
    # Renderiza la plantilla 'estadisticas_pingpong.html' para mostrar las estadísticas de ping pong
    return render(request, 'estadisticas/estadisticas_pingpong.html')

def estadisticas_tenis(request):
    # Renderiza la plantilla 'estadisticas_tenis.html' para mostrar las estadísticas de tenis
    return render(request, 'estadisticas/estadisticas_tenis.html')

def estadisticas_videojuegos(request):
    # Renderiza la plantilla 'estadisticas_videojuegos.html' para mostrar las estadísticas de videojuegos
    return render(request, 'estadisticas/estadisticas_videojuegos.html')

# ========================
# TRANSMISIONES
# ========================

def listar_transmisiones(request):
    # Obtiene todas las transmisiones registradas en la base de datos
    transmisiones = Transmision.objects.all()
    # Ordena las transmisiones por campeonato y nombre
    return render(request, 'transmision/listar_transmisiones.html', {'transmisiones': transmisiones})

def registrar_transmision(request):
    # Verifica si la solicitud es POST (envío de formulario)
    if request.method == 'POST':
        # Obtiene los datos del formulario
        nombre = request.POST.get('nombre')
        # Obtiene la URL de la transmisión
        url = request.POST.get('url')
        # Obtiene el ID del campeonato desde la solicitud POST
        campeonato_id = request.POST.get('campeonato')
        # Verifica si todos los campos son obligatorios
        campeonato = get_object_or_404(Campeonato, id=campeonato_id)
        # Si todos los campos son válidos, crea una nueva transmisión
        Transmision.objects.create(nombre=nombre, url=url, campeonato=campeonato)
        # Muestra un mensaje de éxito al usuario
        return redirect('listar_transmisiones')
    campeonatos = Campeonato.objects.all()
    return render(request, 'transmision/registrar_transmision.html', {'campeonatos': campeonatos})

def detalle_transmision(request, id):
    # Obtiene la transmisión por su ID, o devuelve un error 404 si no se encuentra
    transmision = get_object_or_404(Transmision, id=id)
    # Renderiza la plantilla 'detalle_transmision.html' con la transmisión
    return render(request, 'transmision/detalle_transmision.html', {'transmision': transmision})
# Editar una transmisión (solo admin)
@login_required
@user_passes_test(es_admin)
def editar_transmision(request, id):
    # Obtiene la transmisión por su ID, o devuelve un error 404 si no se encuentra
    transmision = get_object_or_404(Transmision, id=id)

    if request.method == 'POST':
        # Si la solicitud es POST, obtiene los datos del formulario
        nombre = request.POST.get('nombre')
        # Obtiene la URL de la transmisión
        url = request.POST.get('url')
        # Obtiene el ID del campeonato desde la solicitud POST
        campeonato_id = request.POST.get('campeonato')

        if nombre and url and campeonato_id:
            # Verifica si todos los campos son obligatorios
            transmision.nombre = nombre
            # Actualiza la URL de la transmisión
            transmision.url = url
            # Obtiene el campeonato correspondiente al ID proporcionado
            transmision.campeonato = get_object_or_404(Campeonato, id=campeonato_id)
            # Guarda los cambios en la transmisión
            transmision.save()
            # Muestra un mensaje de éxito al usuario
            messages.success(request, 'Transmisión actualizada correctamente.')
            # Redirige al usuario a la lista de transmisiones
            return redirect('listar_transmisiones')
        else:
            # Si algún campo está vacío, muestra un mensaje de error
            messages.error(request, 'Todos los campos son obligatorios.')

    campeonatos = Campeonato.objects.all()
    # Si la solicitud no es POST, crea un formulario con los datos de la transmisión existente
    return render(request, 'transmision/editar_transmision.html', {
        
        'transmision': transmision,
        'campeonatos': campeonatos
    })
# Eliminar una transmisión (solo admin)
@login_required
@user_passes_test(es_admin)
# función para eliminar una transmisión
def eliminar_transmision(request, id):  
    # Obtiene la transmisión por su ID, o devuelve un error 404 si no se encuentra
    transmision = get_object_or_404(Transmision, id=id)

    # Verifica si la solicitud es POST (confirmación de eliminación)
    if request.method == 'POST':
        # Si la solicitud es POST, elimina la transmisión de la base de datos
        transmision.delete()
        # Muestra un mensaje de éxito al usuario
        messages.success(request, 'Transmisión eliminada correctamente.')
        # Redirige al usuario a la lista de transmisiones
        return redirect('listar_transmisiones')

    return render(request, 'transmision/eliminar_transmision.html', {
        # Renderiza la plantilla de confirmación de eliminación con la transmisión
        'transmision': transmision
    })

@login_required
@user_passes_test(es_admin)
# Vista para crear un nuevo usuario administrador
def crear_usuario_admin(request):
    # Verifica si la solicitud es POST (envío de formulario)
    if request.method == 'POST':
        # Crea una instancia del formulario CrearUsuarioAdminForm con los datos enviados
        form = CrearUsuarioAdminForm(request.POST)
        # Verifica si el formulario es válido
        if form.is_valid():
            # Si el formulario es válido, guarda el nuevo usuario administrador
            user = form.save()
            # Asigna el rol de 'ADMIN' al nuevo usuario
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('admin_dashboard')
    else:
        # Si la solicitud no es POST, crea un formulario vacío
        form = CrearUsuarioAdminForm()
    # Renderiza la plantilla 'crear_usuario_admin.html' con el formulario
    return render(request, 'admin_panel/registro_usuario.html', {'form': form})
