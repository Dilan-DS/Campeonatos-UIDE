from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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