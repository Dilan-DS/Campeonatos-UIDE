from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from core.models import Suspension
from core.forms import SuspensionForm
from django.contrib.auth.decorators import login_required, user_passes_test
from core.permisos import es_admin_o_delegado



# ========================
# SUSPENSIONES
# ========================

def _suspensiones_visibles(usuario):
    """Suspensiones que puede ver este usuario.

    Un expediente disciplinario lleva el nombre del jugador y el motivo de
    la sancion, asi que no debe ser publico: estas dos vistas no tenian
    ninguna comprobacion y respondian 200 a un anonimo, exponiendo quien
    esta sancionado y por que.

    ADMIN, DELEGADO y ARBITRO siguen viendo el listado completo, que es lo
    que necesitan para gestionar. Un JUGADOR solo ve el suyo.
    """
    consulta = Suspension.objects.select_related('jugador__usuario', 'jugador__equipo')
    if getattr(usuario, "rol", "") in ("ADMIN", "DELEGADO", "ARBITRO"):
        return consulta
    return consulta.filter(jugador__usuario=usuario)


@login_required
def listar_suspensiones(request):
    suspensiones = _suspensiones_visibles(request.user)
    return render(request, 'suspension/listar.html', {'suspensiones': suspensiones})


@login_required
def detalle_suspension(request, suspension_id):
    # Se busca dentro de lo que este usuario puede ver, de modo que pedir
    # el id de un expediente ajeno devuelve 404 y no lo confirma.
    suspension = get_object_or_404(_suspensiones_visibles(request.user), id=suspension_id)
    return render(request, 'suspension/detalle.html', {'suspension': suspension})

@login_required
@user_passes_test(es_admin_o_delegado)
def registrar_suspension(request):
    # Verifica si la solicitud es POST (envío de formulario)
    if request.method == 'POST':
        # Crea una instancia del formulario SuspensionForm con los datos enviados
        form = SuspensionForm(request.POST)
        # Verifica si el formulario es válido
        if form.is_valid():
            # Guarda el formulario, lo que crea un nuevo objeto Suspension en la base de datos
            form.save()
            # Muestra un mensaje de éxito al usuario
            messages.success(request, "Suspensión registrada correctamente.")
            # Redirige al usuario a la lista de suspensiones
            return redirect('listar_suspensiones')
    else:
        form = SuspensionForm()
    return render(request, 'suspension/registrar.html', {'form': form})