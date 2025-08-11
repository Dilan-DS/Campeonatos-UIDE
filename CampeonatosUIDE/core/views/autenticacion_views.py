from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from core.forms import RegistroUsuarioPublicoForm

def _redir_por_rol(user):
    if getattr(user, 'rol', None) == 'ADMIN':
        return redirect('admin_dashboard')
    elif getattr(user, 'rol', None) == 'DELEGADO':
        return redirect('delegado_dashboard')
    elif getattr(user, 'rol', None) == 'JUGADOR':
        return redirect('jugador_dashboard')
    # Home real del proyecto (ajusta solo si en core/urls.py tiene otro name)
    return redirect('vista_inicio')

def vista_login(request):
    # Si ya está autenticado, redirige por rol
    if request.user.is_authenticated:
        return _redir_por_rol(request.user)

    # Mostrar formulario en GET / procesar en POST
    form = AuthenticationForm(request, data=(request.POST if request.method == 'POST' else None))
    if request.method == 'POST' and form.is_valid():
        usuario = form.get_user()
        login(request, usuario)
        return _redir_por_rol(usuario)

    # SIEMPRE devolver algo en GET o POST inválido
    return render(request, 'usuario/login.html', {'form': form})
        

# Función para registrar un nuevo jugador
def vista_registro(request):
    # Si ya está autenticado, redirige por rol
    if request.user.is_authenticated:
        return _redir_por_rol(request.user)

    # Crea una instancia del formulario de registro de jugador
    form = RegistroUsuarioPublicoForm(request.POST or None)

    # Si el formulario es válido, guarda el nuevo usuario y lo autentica
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        # Redirige según el rol del usuario
        if user.rol == 'JUGADOR':
            return redirect('completar_perfil_jugador')
        return _redir_por_rol(user)

    # SIEMPRE devolver algo en GET o POST inválido
    return render(request, 'usuario/registro.html', {'form': form})

# Función para cerrar sesión
def vista_logout(request):
    # Cierra la sesión del usuario actual
    logout(request)
    # Muestra un mensaje de éxito al usuario
    return redirect('login')
