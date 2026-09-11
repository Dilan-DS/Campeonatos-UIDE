from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.views import View
from core.models import Transmision, Campeonato, Partido
from core.forms import TransmisionForm
from core.permisos import es_admin_o_delegado

# Listar todas las transmisiones
class ListarTransmisionView(View): # Removed LoginRequiredMixin as it will be applied via decorator in urls.py if needed
    def get(self, request):
        transmisiones = Transmision.objects.all()
        return render(request, 'transmision/listar_transmisiones.html', {
            'transmisiones': transmisiones
        })

@login_required
@user_passes_test(es_admin_o_delegado)
def upsert_transmision(request, pk=None):
    """ Unifica crear y editar.
    - Si pk es None: crear
    - Si pk tiene valor: editar
    Renderiza SIEMPRE: transmision/registrar_transmision.html
    """
    obj = get_object_or_404(Transmision, pk=pk) if pk else None
    if request.method == 'POST':
        form = TransmisionForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            obj = form.save()
            messages.success(
                request, 'Transmisión {} correctamente.'.format('actualizada' if pk else 'creada')
            )
            return redirect('listar_transmisiones')
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = TransmisionForm(instance=obj)
    
    ctx = {
        'form': form,
        'es_edicion': bool(pk),
        'obj': obj,
    }
    return render(request, 'transmision/registrar_transmision.html', ctx)

@login_required
@user_passes_test(es_admin_o_delegado)
@require_POST
def eliminar_transmision(request, pk):
    """ Elimina por POST sin plantilla.
    Debes disparar este POST desde un <form> con {% csrf_token %}.
    """
    obj = get_object_or_404(Transmision, pk=pk)
    obj.delete()
    messages.success(request, 'Transmisión eliminada.')
    return redirect('listar_transmisiones')

# Ver detalles de una transmisión
class DetalleTransmisionView(View): # Removed LoginRequiredMixin as it will be applied via decorator in urls.py if needed
    def get(self, request, id):
        transmision = get_object_or_404(Transmision, id=id)
        return render(request, 'transmision/detalle_transmision.html', {
            'transmision': transmision,
        })
