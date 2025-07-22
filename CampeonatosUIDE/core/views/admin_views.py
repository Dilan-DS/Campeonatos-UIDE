from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.forms import *
from core.models import *
from django.http import HttpResponse
from django.db.models import Q
from datetime import datetime, timedelta



def es_admin(user):
    # Verifica si el usuario es un administrador
    return user.rol == 'ADMIN'

@login_required
@user_passes_test(es_admin)
# función para el dashboard del administrador
def admin_dashboard(request):
    # Renderiza la plantilla 'admin.html' para el dashboard del administrador
    return render(request, 'dashboard/admin.html')
@login_required
@user_passes_test(es_admin)
def listar_usuarios(request):
    query = request.GET.get('buscar', '')
    if query:
        usuarios = Usuario.objects.filter(
            Q(username__icontains=query) | Q(cedula__icontains=query)
        )
    else:
        usuarios = Usuario.objects.all()

    return render(request, 'usuario/admin_listar.html', {
        'usuarios': usuarios,
        'query': query
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

@login_required
@user_passes_test(es_admin)
def registrar_delegado(request):
    if request.method == 'POST':
        form = CrearUsuarioDelegadoForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.rol = 'DELEGADO'
            user.set_password(form.cleaned_data['password'])  # Asegura que la contraseña se guarde hasheada
            user.save()
            messages.success(request, 'Delegado creado exitosamente.')
            return redirect('admin_dashboard')
    else:
        form = CrearUsuarioDelegadoForm()
    return render(request, 'admin_panel/registro_delegado.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuario/editar_admin.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")
        return redirect('listar_usuarios')
    return render(request, 'usuario/confirmar_eliminacion_admin.html', {'usuario': usuario})


@login_required
@user_passes_test(es_admin)
def generar_calendario(request, campeonato_id):
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)
    equipos = Equipo.objects.filter(campeonato=campeonato)
    
    if equipos.count() < 2:
        messages.warning(request, "Debe haber al menos 2 equipos para generar el calendario.")
        return redirect('listar_campeonatos')

    # Limpia partidos anteriores del campeonato
    Partido.objects.filter(campeonato=campeonato).delete()

    fecha_inicial = datetime.today().date()
    hora_base = datetime.strptime('10:00', '%H:%M').time()
    dia_offset = 0

    partidos_creados = []
    for i in range(len(equipos)):
        for j in range(i + 1, len(equipos)):
            partido = Partido.objects.create(
                campeonato=campeonato,
                equipo_local=equipos[i],
                equipo_visitante=equipos[j],
                fecha=fecha_inicial + timedelta(days=dia_offset),
                hora=hora_base,
                cancha='Cancha UIDE'
            )
            partidos_creados.append(partido)
            dia_offset += 1

    messages.success(request, f"Fixture generado con {len(partidos_creados)} partidos.")
    return redirect('listar_partidos_campeonato', campeonato_id=campeonato.id)