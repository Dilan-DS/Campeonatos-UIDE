# Importa la clase base para vistas basadas en clases (CBV)
from django.views import View
# Funciones para renderizar templates, redirigir y obtener objetos o lanzar 404
from django.shortcuts import render, redirect, get_object_or_404
# Sistema de mensajes para feedback al usuario
from django.contrib import messages
# Herramientas para realizar consultas complejas (Q) en ORM
from django.db.models import Q
# Manejo de errores de validación para modelos
from django.core.exceptions import ValidationError
# Importa el modelo CodigoQR de la aplicación core
from core.models import CodigoQR
# Importa el formulario CodigoQRForm para manejar los datos de códigos QR
from core.forms import CodigoQRForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

def es_admin(user):
    return user.rol == 'ADMIN'


# Vista para listar códigos QR con opción de búsqueda
class ListarCodigosQRView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return es_admin(self.request.user)
    # Método GET que recibe posibles parámetros de búsqueda
    def get(self, request):
        # Obtiene el parámetro 'q' de la URL, valor vacío si no existe
        query = request.GET.get("q", "")
        # Si hay consulta, filtra por banco o descripción que contengan el texto (insensible a mayúsculas)
        if query:
            codigos_qr = CodigoQR.objects.filter(
                Q(banco__icontains=query) | Q(descripcion__icontains=query)
            )
        else:
            # Si no hay búsqueda, obtiene todos los códigos QR
            codigos_qr = CodigoQR.objects.all()
        # Renderiza el template con los códigos QR resultantes
        return render(request, 'codigoqr/listar.html', {
            'codigos_qr': codigos_qr
        })


# Vista para registrar un nuevo código QR
class RegistrarCodigoQRView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return es_admin(self.request.user)
    # Método GET que muestra un formulario vacío
    def get(self, request):
        # Instancia vacía del formulario
        form = CodigoQRForm()
        # Renderiza el template con el formulario y modo crear
        return render(request, 'codigoqr/registrar.html', {
            'form': form,
            'modo': 'crear'
        })

    # Método POST que procesa el formulario enviado
    def post(self, request):
        # Instancia del formulario con datos y archivos enviados
        form = CodigoQRForm(request.POST, request.FILES)
        # Valida el formulario
        if form.is_valid():
            # Guarda el nuevo código QR en la base de datos
            form.save()
            # Mensaje de éxito para el usuario
            messages.success(request, "Código QR registrado con éxito.")
            # Redirige a la lista de códigos QR
            return redirect('listar_codigos_qr')
        # Si no es válido, vuelve a mostrar el formulario con errores
        return render(request, 'codigoqr/registrar.html', {
            'form': form,
            'modo': 'crear'
        })


# Vista para editar un código QR existente con actualización manual
class EditarCodigoQRView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return es_admin(self.request.user)
    # Método GET que muestra formulario con datos del código QR
    def get(self, request, pk):
        # Obtiene el código QR o 404 si no existe
        codigo = get_object_or_404(CodigoQR, pk=pk)
        # Instancia del formulario rellenado con datos actuales
        form = CodigoQRForm(instance=codigo)
        # Renderiza el template con formulario, código y modo editar
        return render(request, 'codigoqr/registrar.html', {
            'form': form,
            'codigo': codigo,
            'modo': 'editar'
        })

    # Método POST que procesa la edición
    def post(self, request, pk):
        # Obtiene el código QR o 404
        codigo = get_object_or_404(CodigoQR, pk=pk)
        # Instancia del formulario con datos enviados y archivos, ligado al objeto a actualizar
        form = CodigoQRForm(request.POST, request.FILES, instance=codigo)

        # Valida el formulario
        if form.is_valid():
            form.save()
            # Mensaje de éxito
            messages.success(request, "Código QR actualizado correctamente.")
            # Redirige a la lista de códigos QR
            return redirect('listar_codigos_qr')

        # Si no válido, vuelve a mostrar el formulario con errores y datos actuales
        return render(request, 'codigoqr/registrar.html', {
            'form': form,
            'codigo': codigo,
            'modo': 'editar'
        })


# Vista para mostrar detalle de un código QR
class DetalleCodigoQRView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return es_admin(self.request.user)
    # Método GET que muestra la información del código QR en modo detalle
    def get(self, request, pk):
        # Obtiene el código QR o 404
        codigo = get_object_or_404(CodigoQR, pk=pk)
        # Renderiza el template con modo detalle
        return render(request, 'codigoqr/registrar.html', {
            'codigo': codigo,
            'modo': 'detalle'
        })


# Vista para eliminar un código QR con confirmación
class EliminarCodigoQRView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return es_admin(self.request.user)
    # Método GET que muestra confirmación de eliminación
    def get(self, request, pk):
        # Obtiene el código QR o 404
        codigo = get_object_or_404(CodigoQR, pk=pk)
        # Renderiza el template con modo eliminar
        return render(request, 'codigoqr/registrar.html', {
            'codigo': codigo,
            'modo': 'eliminar'
        })

    # Método POST que elimina el código QR tras confirmación
    def post(self, request, pk):
        # Obtiene el código QR o 404
        codigo = get_object_or_404(CodigoQR, pk=pk)
        # Elimina el objeto de la base de datos
        codigo.delete()
        # Mensaje de éxito al usuario
        messages.success(request, "Código QR eliminado correctamente.")
        # Redirige a la lista de códigos QR
        return redirect('listar_codigos_qr')
