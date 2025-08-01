from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Partido
from core.forms import PartidoForm
from core.views.admin_views import es_admin

# Función para validar que sea admin
def es_admin(user):
    return user.rol == 'ADMIN'

@login_required
@user_passes_test(es_admin)
def listar_partidos(request):
    # Obtiene todos los partidos registrados en la base de datos y los ordena por fecha y hora
    partidos = Partido.objects.all().order_by('-fecha', '-hora')
    # Renderiza la plantilla 'listar_partidos.html' con los partidos
    return render(request, 'partido/listar_partidos.html', {'partidos': partidos})


@login_required
@user_passes_test(es_admin)
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


@login_required
@user_passes_test(es_admin)
def detalle_partido(request, partido_id):
    # Obtiene el partido por su ID, o devuelve un error 404 si no se encuentra
    partido = get_object_or_404(Partido, id=partido_id)
    # Verifica si el partido tiene un campeonato asociado
    return render(request, 'partido/detalle_partido.html', {'partido': partido})


@login_required
@user_passes_test(es_admin)
def editar_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    
    if request.method == 'POST':
        form = PartidoForm(request.POST, instance=partido)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partido actualizado correctamente.')
            return redirect('detalle_partido', partido_id=partido.id)
    else:
        form = PartidoForm(instance=partido)
    
    return render(request, 'partido/editar_partido.html', {'form': form, 'partido': partido})

@login_required
@user_passes_test(es_admin)
def eliminar_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    
    if request.method == 'POST':
        partido.delete()
        messages.success(request, 'Partido eliminado correctamente.')
        return redirect('listar_partidos')
    
    return render(request, 'partido/eliminar_partido.html', {'partido': partido})


@login_required
@user_passes_test(es_admin)
def aplazar_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)

    if request.method == 'POST':
        form = PartidoForm(request.POST, instance=partido)
        if form.is_valid():
            nuevo_partido = form.save(commit=False)
            # Aquí podrías registrar el cambio o validar reglas de aplazamiento
            nuevo_partido.save()
            messages.success(request, 'Partido aplazado exitosamente.')
            return redirect('detalle_partido', partido_id=partido.id)
    else:
        form = PartidoForm(instance=partido)

    return render(request, 'partido/aplazar_partido.html', {'form': form, 'partido': partido})

@login_required
@user_passes_test(es_admin)
def ver_calendario_completo(request):
    # Placeholder function for now
    return render(request, 'partido/calendario_completo.html', {})
