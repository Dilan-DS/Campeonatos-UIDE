from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import ValidationError
from core.models import CodigoQR
from core.forms import CodigoQRForm


# LISTAR con búsqueda
class ListarCodigosQRView(View):
    def get(self, request):
        query = request.GET.get("q", "")
        if query:
            codigos_qr = CodigoQR.objects.filter(
                Q(banco__icontains=query) | Q(descripcion__icontains=query)
            )
        else:
            codigos_qr = CodigoQR.objects.all()
        return render(request, 'codigoqr/listar.html', {
            'codigos_qr': codigos_qr
        })


# REGISTRAR nuevo QR
class RegistrarCodigoQRView(View):
    def get(self, request):
        form = CodigoQRForm()
        return render(request, 'codigoqr/registrar.html', {
            'form': form,
            'modo': 'crear'
        })

    def post(self, request):
        form = CodigoQRForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Código QR registrado con éxito.")
            return redirect('listar_codigos_qr')
        return render(request, 'codigoqr/registrar.html', {
            'form': form,
            'modo': 'crear'
        })


# EDITAR QR (actualización manual)
class EditarCodigoQRView(View):
    def get(self, request, pk):
        codigo = get_object_or_404(CodigoQR, pk=pk)
        form = CodigoQRForm(instance=codigo)
        return render(request, 'codigoqr/registrar.html', {
            'form': form,
            'codigo': codigo,
            'modo': 'editar'
        })

    def post(self, request, pk):
        codigo = get_object_or_404(CodigoQR, pk=pk)
        form = CodigoQRForm(request.POST, request.FILES, instance=codigo)

        if form.is_valid():
            datos = form.cleaned_data

            # Actualizar manualmente los campos
            codigo.banco = datos.get('banco', codigo.banco)
            codigo.descripcion = datos.get('descripcion', codigo.descripcion)

            if request.FILES.get('imagen_qr'):
                codigo.imagen_qr = request.FILES['imagen_qr']

            try:
                codigo.full_clean()
                codigo.save()
                messages.success(request, "Código QR actualizado correctamente.")
                return redirect('listar_codigos_qr')
            except ValidationError as e:
                form.add_error(None, e)

        return render(request, 'codigoqr/registrar.html', {
            'form': form,
            'codigo': codigo,
            'modo': 'editar'
        })


# DETALLE QR
class DetalleCodigoQRView(View):
    def get(self, request, pk):
        codigo = get_object_or_404(CodigoQR, pk=pk)
        return render(request, 'codigoqr/registrar.html', {
            'codigo': codigo,
            'modo': 'detalle'
        })


# ELIMINAR QR con confirmación
class EliminarCodigoQRView(View):
    def get(self, request, pk):
        codigo = get_object_or_404(CodigoQR, pk=pk)
        return render(request, 'codigoqr/registrar.html', {
            'codigo': codigo,
            'modo': 'eliminar'
        })

    def post(self, request, pk):
        codigo = get_object_or_404(CodigoQR, pk=pk)
        codigo.delete()
        messages.success(request, "Código QR eliminado correctamente.")
        return redirect('listar_codigos_qr')
