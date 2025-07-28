# Importa la clase base para crear vistas basadas en clases (CBV)
from django.views import View
# Funciones para renderizar plantillas, redireccionar y obtener objetos o lanzar error 404
from django.shortcuts import render, redirect, get_object_or_404
# Sistema de mensajes para enviar notificaciones al usuario
from django.contrib import messages
# Decoradores para exigir que el usuario esté autenticado y tenga ciertos permisos
from django.contrib.auth.decorators import login_required, user_passes_test
# Permite aplicar decoradores a métodos de vistas basadas en clases
from django.utils.decorators import method_decorator
# Importa el modelo Deporte de la aplicación core
from core.models import Deporte
# Importa el formulario para manejar datos de Deporte
from core.forms import DeporteForm


# Función para verificar si el usuario tiene rol de administrador
def es_admin(user):
    # Retorna True si el atributo rol del usuario es 'ADMIN'
    return user.rol == 'ADMIN'


# Lista de decoradores que exigen login y que el usuario sea admin
decoradores_admin = [login_required, user_passes_test(es_admin)]


# Clase para listar todos los deportes, protegida por decoradores admin
@method_decorator(decoradores_admin, name='dispatch')
class ListarDeportesView(View):
    # Método GET que obtiene todos los objetos Deporte
    def get(self, request):
        deportes = Deporte.objects.all()
        # Renderiza la plantilla con la lista de deportes
        return render(request, 'deporte/listar_deportes.html', {
            'deportes': deportes
        })


# Clase para registrar un nuevo deporte, protegida por decoradores admin
@method_decorator(decoradores_admin, name='dispatch')
class RegistrarDeporteView(View):
    # Método GET que muestra un formulario vacío para crear deporte
    def get(self, request):
        form = DeporteForm()
        # Renderiza el formulario con modo crear
        return render(request, 'deporte/registrar.html', {
            'form': form,
            'modo': 'crear'
        })

    # Método POST que procesa el formulario enviado para crear deporte
    def post(self, request):
        form = DeporteForm(request.POST)
        # Valida el formulario
        if form.is_valid():
            # Guarda el nuevo deporte en la base de datos
            form.save()
            # Muestra mensaje de éxito
            messages.success(request, "Deporte registrado exitosamente.")
            # Redirige a la lista de deportes
            return redirect('listar_deportes')
        # Si hay errores, renderiza de nuevo el formulario con errores y modo crear
        return render(request, 'deporte/registrar.html', {
            'form': form,
            'modo': 'crear'
        })


# Clase para editar un deporte existente, con actualización manual, protegida por admin
@method_decorator(decoradores_admin, name='dispatch')
class EditarDeporteView(View):
    # Método GET que carga el deporte a editar y muestra el formulario con datos actuales
    def get(self, request, id):
        deporte = get_object_or_404(Deporte, id=id)
        form = DeporteForm(instance=deporte)
        # Renderiza el formulario con modo editar y el objeto deporte
        return render(request, 'deporte/registrar.html', {
            'form': form,
            'modo': 'editar',
            'deporte': deporte
        })

    # Método POST que procesa la edición con datos enviados
    def post(self, request, id):
        deporte = get_object_or_404(Deporte, id=id)
        form = DeporteForm(request.POST, instance=deporte)

        # Valida el formulario
        if form.is_valid():
            # Obtiene los datos limpios del formulario
            datos = form.cleaned_data
            # Actualiza manualmente los campos del objeto deporte
            deporte.nombre = datos.get('nombre', deporte.nombre)
            deporte.descripcion = datos.get('descripcion', deporte.descripcion)
            # Guarda los cambios en la base de datos
            deporte.save()
            # Mensaje de éxito al usuario
            messages.success(request, "Deporte actualizado correctamente.")
            # Redirige a la lista de deportes
            return redirect('listar_deportes')

        # Si no válido, renderiza el formulario con errores, modo editar y objeto deporte
        return render(request, 'deporte/registrar.html', {
            'form': form,
            'modo': 'editar',
            'deporte': deporte
        })


# Clase para eliminar un deporte, protegida por admin
@method_decorator(decoradores_admin, name='dispatch')
class EliminarDeporteView(View):
    # Método GET que muestra confirmación de eliminación
    def get(self, request, id):
        deporte = get_object_or_404(Deporte, id=id)
        # Renderiza el template con modo eliminar y objeto deporte
        return render(request, 'deporte/registrar.html', {
            'deporte': deporte,
            'modo': 'eliminar'
        })

    # Método POST que elimina el deporte tras confirmación
    def post(self, request, id):
        deporte = get_object_or_404(Deporte, id=id)
        # Elimina el objeto de la base de datos
        deporte.delete()
        # Mensaje de éxito al usuario
        messages.success(request, "Deporte eliminado correctamente.")
        # Redirige a la lista de deportes
        return redirect('listar_deportes')
