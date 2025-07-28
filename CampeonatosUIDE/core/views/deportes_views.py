from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from core.models import Deporte
from core.forms import DeporteForm


# Verificación de rol administrador
def es_admin(user):
    return user.rol == 'ADMIN'


# Decorador para proteger las vistas con login y rol
decoradores_admin = [login_required, user_passes_test(es_admin)]


# ========== LISTAR ==========
@method_decorator(decoradores_admin, name='dispatch')
class ListarDeportesView(View):
    def get(self, request):
        deportes = Deporte.objects.all()
        return render(request, 'deporte/listar_deportes.html', {
            'deportes': deportes
        })


# ========== REGISTRAR ==========
@method_decorator(decoradores_admin, name='dispatch')
class RegistrarDeporteView(View):
    def get(self, request):
        form = DeporteForm()
        return render(request, 'deporte/registrar.html', {
            'form': form,
            'modo': 'crear'
        })

    def post(self, request):
        form = DeporteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Deporte registrado exitosamente.")
            return redirect('listar_deportes')
        return render(request, 'deporte/registrar.html', {
            'form': form,
            'modo': 'crear'
        })


# ========== EDITAR (MANUAL) ==========
@method_decorator(decoradores_admin, name='dispatch')
class EditarDeporteView(View):
    def get(self, request, id):
        deporte = get_object_or_404(Deporte, id=id)
        form = DeporteForm(instance=deporte)
        return render(request, 'deporte/registrar.html', {
            'form': form,
            'modo': 'editar',
            'deporte': deporte
        })

    def post(self, request, id):
        deporte = get_object_or_404(Deporte, id=id)
        form = DeporteForm(request.POST, instance=deporte)

        if form.is_valid():
            datos = form.cleaned_data
            deporte.nombre = datos.get('nombre', deporte.nombre)
            deporte.descripcion = datos.get('descripcion', deporte.descripcion)
            deporte.save()
            messages.success(request, "Deporte actualizado correctamente.")
            return redirect('listar_deportes')

        return render(request, 'deporte/registrar.html', {
            'form': form,
            'modo': 'editar',
            'deporte': deporte
        })


# ========== ELIMINAR ==========
@method_decorator(decoradores_admin, name='dispatch')
class EliminarDeporteView(View):
    def get(self, request, id):
        deporte = get_object_or_404(Deporte, id=id)
        return render(request, 'deporte/registrar.html', {
            'deporte': deporte,
            'modo': 'eliminar'
        })

    def post(self, request, id):
        deporte = get_object_or_404(Deporte, id=id)
        deporte.delete()
        messages.success(request, "Deporte eliminado correctamente.")
        return redirect('listar_deportes')
