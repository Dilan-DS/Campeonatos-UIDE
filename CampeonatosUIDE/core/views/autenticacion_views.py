from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from core.forms import RegistroUsuarioPublicoForm


def vista_login(request):
    if request.user.is_authenticated:
        if request.user.rol == 'ADMIN':
            return redirect('admin_dashboard')
        elif request.user.rol == 'DELEGADO':
            return redirect('delegado_dashboard')
        elif request.user.rol == 'JUGADOR':
            return redirect('jugador_dashboard')
        return redirect('vista_inicio')
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        usuario = form.get_user()
        login(request, usuario)
        if usuario.rol == 'ADMIN':
            return redirect('admin_dashboard')
        elif usuario.rol == 'DELEGADO':
            return redirect('delegado_dashboard')
        elif usuario.rol == 'JUGADOR':
            return redirect('jugador_dashboard')
        return redirect('vista_inicio')
    return render(request, 'usuario/login.html', {'form': form})

# Función para registrar un nuevo jugador
def vista_registro(request):
    if request.user.is_authenticated:
        if request.user.rol == 'ADMIN':
            return redirect('admin_dashboard')
        elif request.user.rol == 'DELEGADO':
            return redirect('delegado_dashboard')
        elif request.user.rol == 'JUGADOR':
            return redirect('jugador_dashboard')
        return redirect('vista_inicio')
    # Crea una instancia del formulario de registro de jugador
    form = RegistroUsuarioPublicoForm(request.POST or None)
    # Si el formulario es válido, guarda el nuevo usuario y lo autentica
    if form.is_valid():
        # Guarda el formulario, lo que crea un nuevo usuario
        user = form.save()
        # Asigna el rol de 'JUGADOR' al nuevo usuario
        login(request, user)

        # Redirige según el rol del usuario
        if user.rol == 'DELEGADO':
            return redirect('delegado_dashboard')
        elif user.rol == 'JUGADOR':
            return redirect('completar_perfil_jugador')
        else:
            return redirect('jugador_dashboard')  

    return render(request, 'usuario/registro.html', {'form': form})

# Función para cerrar sesión
def vista_logout(request):
    # Cierra la sesión del usuario actual
    logout(request)
    # Muestra un mensaje de éxito al usuario
    return redirect('login')
