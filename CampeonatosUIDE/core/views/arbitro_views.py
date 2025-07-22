from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Arbitro
from core.forms import ArbitroForm


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
