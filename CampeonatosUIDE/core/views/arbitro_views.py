# Importa funciones para renderizar templates, redireccionar y obtener objetos o error 404 si no existen
from django.shortcuts import render, redirect, get_object_or_404
# Importa la clase base para vistas basadas en clases (CBV)
from django.views import View
# Importa el sistema de mensajes para mostrar alertas al usuario
from django.contrib import messages
# Importa el modelo Arbitro de la aplicación core
from core.models import Arbitro
# Importa el formulario ArbitroForm para manipular datos de árbitros
from core.forms import ArbitroForm

# ========================
# CLASES BASADAS EN VISTAS (CBV) - ÁRBITROS
# ========================

# Clase para listar todos los árbitros
class listar_arbitros(View):
    # Método GET que maneja la solicitud de la página para mostrar árbitros
    def get(self, request):
        # Obtiene todos los objetos Arbitro de la base de datos
        arbitros = Arbitro.objects.all()
        # Renderiza el template 'arbitro/listar.html' enviando la lista de árbitros
        return render(request, 'arbitro/listar.html', {
            'arbitros': arbitros
        })


# Clase para registrar un nuevo árbitro
class registrar_arbitro(View):
    # Método GET que muestra el formulario vacío para registrar árbitro
    def get(self, request):
        # Crea una instancia vacía del formulario ArbitroForm
        form = ArbitroForm()
        # Renderiza el template con el formulario y un modo para identificar la acción
        return render(request, 'arbitro/registrar.html', {
            'form': form,
            'modo': 'crear'
        })

    # Método POST que procesa el formulario enviado para crear árbitro
    def post(self, request):
        # Crea una instancia del formulario con los datos enviados
        form = ArbitroForm(request.POST)
        # Verifica que el formulario sea válido
        if form.is_valid():
            # Guarda el nuevo árbitro en la base de datos
            form.save()
            # Muestra mensaje de éxito al usuario
            messages.success(request, 'Árbitro registrado correctamente')
            # Redirige al listado de árbitros
            return redirect('listar_arbitros')
        # Si el formulario no es válido, vuelve a mostrar el formulario con errores
        return render(request, 'arbitro/registrar.html', {
            'form': form,
            'modo': 'crear'
        })


# Clase para editar un árbitro existente
class editar_arbitro(View):
    # Método GET que muestra el formulario con datos del árbitro para editar
    def get(self, request, id):
        # Obtiene el árbitro por su id o lanza 404 si no existe
        arbitro = get_object_or_404(Arbitro, id=id)
        # Crea el formulario rellenado con los datos actuales del árbitro
        form = ArbitroForm(instance=arbitro)
        # Renderiza el template con el formulario, el árbitro y modo edición
        return render(request, 'arbitro/registrar.html', {
            'form': form,
            'arbitro': arbitro,
            'modo': 'editar'
        })

    # Método POST que procesa el formulario con datos para actualizar árbitro
    def post(self, request, id):
        # Obtiene el árbitro a editar o error 404
        arbitro = get_object_or_404(Arbitro, id=id)
        # Crea el formulario con los datos enviados, pero no pasa la instancia para evitar errores
        form = ArbitroForm(request.POST)
        # Valida el formulario
        if form.is_valid():
            # Actualiza manualmente los campos del árbitro con los datos limpios del formulario
            arbitro.nombre = form.cleaned_data['nombre']
            arbitro.apellido = form.cleaned_data['apellido']
            arbitro.experiencia = form.cleaned_data['experiencia']
            arbitro.contacto = form.cleaned_data['contacto']
            arbitro.estado = form.cleaned_data['estado']
            # Guarda los cambios en la base de datos
            arbitro.save()
            # Actualiza la relación M2M de deportes asignados al árbitro
            arbitro.deportes.set(form.cleaned_data['deportes'])

            # Mensaje de éxito al usuario
            messages.success(request, 'Árbitro actualizado correctamente')
            # Redirige al listado de árbitros
            return redirect('listar_arbitros')

        # Si el formulario no es válido, renderiza de nuevo con errores
        return render(request, 'arbitro/registrar.html', {
            'form': form,
            'arbitro': arbitro,
            'modo': 'editar'
        })


# Clase para mostrar detalles de un árbitro
class detalle_arbitro(View):
    # Método GET para mostrar información del árbitro
    def get(self, request, id):
        # Obtiene el árbitro o 404
        arbitro = get_object_or_404(Arbitro, id=id)
        # Renderiza el template en modo detalle
        return render(request, 'arbitro/registrar.html', {
            'arbitro': arbitro,
            'modo': 'detalle'
        })


# Clase para eliminar un árbitro
class eliminar_arbitro(View):
    # Método GET que muestra confirmación para eliminar
    def get(self, request, id):
        # Obtiene el árbitro o 404
        arbitro = get_object_or_404(Arbitro, id=id)
        # Renderiza el template en modo eliminar
        return render(request, 'arbitro/registrar.html', {'modo': 'eliminar', 'arbitro': arbitro})

    # Método POST que elimina el árbitro
    def post(self, request, id):
        # Obtiene el árbitro o 404
        arbitro = get_object_or_404(Arbitro, id=id)
        # Elimina el árbitro de la base de datos
        arbitro.delete()
        # Mensaje de éxito al usuario
        messages.success(request, 'Árbitro eliminado correctamente')
        # Redirige al listado de árbitros
        return redirect('listar_arbitros')
