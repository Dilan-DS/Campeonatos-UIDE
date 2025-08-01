from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import ImagenGaleria
from core.forms import ImagenGaleriaForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

def es_admin_o_delegado(user):
    return user.rol in ['ADMIN', 'DELEGADO']

class ListarImagenGaleria(View):
    def get(self, request):
        imagenes = ImagenGaleria.objects.all().order_by('-fecha')
        return render(request, 'galeria/imagen_listar.html', {'imagenes': imagenes})

class RegistrarImagenGaleria(View):
    def get(self, request):
        form = ImagenGaleriaForm()
        return render(request, 'galeria/imagen_form.html', {'form': form, 'modo': 'crear'})

    def post(self, request):
        form = ImagenGaleriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Imagen registrada correctamente.")
            return redirect('listar_imagenes_galeria')
        return render(request, 'galeria/imagen_form.html', {'form': form, 'modo': 'crear'})

class EditarImagenGaleria(View):
    def get(self, request, id):
        imagen = get_object_or_404(ImagenGaleria, id=id)
        form = ImagenGaleriaForm(instance=imagen)
        return render(request, 'galeria/imagen_form.html', {'form': form, 'modo': 'editar', 'imagen': imagen})

    def post(self, request, id):
        imagen = get_object_or_404(ImagenGaleria, id=id)
        form = ImagenGaleriaForm(request.POST, request.FILES, instance=imagen)
        if form.is_valid():
            form.save()
            messages.success(request, "Imagen actualizada correctamente.")
            return redirect('listar_imagenes_galeria')
        return render(request, 'galeria/imagen_form.html', {'form': form, 'modo': 'editar', 'imagen': imagen})

    def test_func(self):
        return self.request.user.rol in ['ADMIN', 'DELEGADO']

class EliminarImagenGaleria(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, id):
        imagen = get_object_or_404(ImagenGaleria, id=id)
        return render(request, 'galeria/imagen_form.html', {'imagen': imagen})

    def post(self, request, id):
        imagen = get_object_or_404(ImagenGaleria, id=id)
        imagen.delete()
        messages.success(request, "Imagen eliminada correctamente.")
        return redirect('listar_imagenes_galeria')
