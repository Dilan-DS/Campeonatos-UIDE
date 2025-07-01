from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Equipo


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
