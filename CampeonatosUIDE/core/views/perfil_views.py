from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.forms import PerfilUsuarioForm

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
    user = request.user
    if request.method == "POST":
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("perfil_usuario")
    else:
        form = PerfilUsuarioForm(instance=user)
    return render(request, "usuario/editar_perfil.html", {"form": form})