from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from core.forms import RegistroJugadorForm


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
