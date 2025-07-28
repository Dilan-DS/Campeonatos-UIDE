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