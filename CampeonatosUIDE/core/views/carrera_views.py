from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from core.models import Carrera
from core.forms import CarreraForm
from core.permisos import es_admin_o_delegado

class ListarCarrerasView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.rol == 'ADMIN'

    def get(self, request):
        carreras = Carrera.objects.all().order_by('nombre')
        return render(request, 'carrera/listar_carrera.html', {'carreras': carreras})

class GestionCarreraView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.rol == 'ADMIN'

    def get(self, request, id=None, action=None):
        carrera = None
        form = None
        modo = 'crear'

        if id:
            carrera = get_object_or_404(Carrera, id=id)
            if action == 'editar':
                form = CarreraForm(instance=carrera)
                modo = 'editar'
            elif action == 'eliminar':
                modo = 'eliminar'
            else: # Default to view if no action specified with ID
                modo = 'ver'
        else:
            form = CarreraForm()

        context = {
            'form': form,
            'carrera': carrera,
            'modo': modo
        }
        return render(request, 'carrera/registrar_carrera.html', context)

    def post(self, request, id=None, action=None):
        # `carrera` solo se asignaba en las ramas 'eliminar' y 'editar': al
        # crear una carrera con datos invalidos (p.ej. nombre duplicado), el
        # contexto final de abajo intentaba leer una variable que nunca se
        # habia definido y la vista terminaba en un 500 (UnboundLocalError)
        # en vez de mostrar el error del formulario.
        carrera = None
        if action == 'eliminar':
            carrera = get_object_or_404(Carrera, id=id)
            carrera.delete()
            messages.success(request, "Carrera eliminada correctamente.")
            return redirect('listar_carreras')
        elif id: # Edit existing
            carrera = get_object_or_404(Carrera, id=id)
            form = CarreraForm(request.POST, instance=carrera)
            if form.is_valid():
                form.save()
                messages.success(request, "Carrera actualizada correctamente.")
                return redirect('listar_carreras')
            modo = 'editar' # If form is invalid, stay in edit mode
        else: # Create new
            form = CarreraForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Carrera registrada correctamente.")
                return redirect('listar_carreras')
            modo = 'crear' # If form is invalid, stay in create mode

        context = {
            'form': form,
            'carrera': carrera,
            'modo': modo
        }
        return render(request, 'carrera/registrar_carrera.html', context)
