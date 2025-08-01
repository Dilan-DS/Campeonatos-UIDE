from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from core.models import Suspension
from core.forms import SuspensionForm
from django.contrib.auth.decorators import login_required, user_passes_test
from core.views.campeonato_views import es_admin_o_delegado



# ========================
# SUSPENSIONES
# ========================

def listar_suspensiones(request):
    # Obtiene todas las suspensiones registradas en la base de datos
    suspensiones = Suspension.objects.select_related('jugador__usuario', 'jugador__equipo').all()
    # Ordena las suspensiones por fecha de inicio en orden descendente
    return render(request, 'suspension/listar.html', {'suspensiones': suspensiones})

def detalle_suspension(request, suspension_id):
    # Obtiene la suspensión por su ID, o devuelve un error 404 si no se encuentra
    suspension = get_object_or_404(Suspension, id=suspension_id)
    # Renderiza la plantilla 'detalle.html' con la suspensión
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