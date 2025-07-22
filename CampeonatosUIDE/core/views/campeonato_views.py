from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Campeonato
from core.forms import CampeonatoForm

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

def campeonatos_publicos(request):
    campeonatos = Campeonato.objects.filter(es_publico=True)
    return render(request, 'campeonato/campeonatos_publicos.html', {'campeonatos': campeonatos})


def campeonatos_publicos(request):
    campeonatos = Campeonato.objects.filter(activo=True)  # o filtra como quieras
    return render(request, 'campeonato/campeonatos_publicos.html', {
        'campeonatos': campeonatos
    })