from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Testimonio
from core.forms import TestimonioForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from core.views.campeonato_views import es_admin_o_delegado

class ListarTestimonios(View):
    def get(self, request):
        testimonios = Testimonio.objects.all().order_by('-creado_en')
        return render(request, 'testimonio/listar.html', {'testimonios': testimonios})

class RegistrarTestimonio(LoginRequiredMixin, UserPassesTestMixin, View):
    """Solo ADMIN y DELEGADO gestionan testimonios.

    Estas tres vistas eran `View` a secas, sin ninguna comprobacion: un
    usuario anonimo podia crear, editar y borrar testimonios. Comprobado
    con peticiones sin sesion antes del arreglo. Se aplica la misma regla
    que ya tenian noticias y galeria.
    """

    def test_func(self):
        return es_admin_o_delegado(self.request.user)

    def get(self, request):
        form = TestimonioForm()
        return render(request, 'testimonio/form.html', {'form': form, 'modo': 'crear'})

    def post(self, request):
        form = TestimonioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonio registrado correctamente.")
            return redirect('listar_testimonios')
        return render(request, 'testimonio/form.html', {'form': form, 'modo': 'crear'})

class EditarTestimonio(LoginRequiredMixin, UserPassesTestMixin, View):
    """Solo ADMIN y DELEGADO gestionan testimonios.

    Estas tres vistas eran `View` a secas, sin ninguna comprobacion: un
    usuario anonimo podia crear, editar y borrar testimonios. Comprobado
    con peticiones sin sesion antes del arreglo. Se aplica la misma regla
    que ya tenian noticias y galeria.
    """

    def test_func(self):
        return es_admin_o_delegado(self.request.user)

    def get(self, request, id):
        testimonio = get_object_or_404(Testimonio, id=id)
        form = TestimonioForm(instance=testimonio)
        return render(request, 'testimonio/form.html', {'form': form, 'modo': 'editar', 'testimonio': testimonio})

    def post(self, request, id):
        testimonio = get_object_or_404(Testimonio, id=id)
        form = TestimonioForm(request.POST, request.FILES, instance=testimonio)
        if form.is_valid():
            form.save()
            messages.success(request, "Testimonio actualizado correctamente.")
            return redirect('listar_testimonios')
        return render(request, 'testimonio/form.html', {'form': form, 'modo': 'editar', 'testimonio': testimonio})

class EliminarTestimonio(LoginRequiredMixin, UserPassesTestMixin, View):
    """Solo ADMIN y DELEGADO gestionan testimonios.

    Estas tres vistas eran `View` a secas, sin ninguna comprobacion: un
    usuario anonimo podia crear, editar y borrar testimonios. Comprobado
    con peticiones sin sesion antes del arreglo. Se aplica la misma regla
    que ya tenian noticias y galeria.
    """

    def test_func(self):
        return es_admin_o_delegado(self.request.user)

    def get(self, request, id):
        testimonio = get_object_or_404(Testimonio, id=id)
        return render(request, 'testimonio/form.html', {'testimonio': testimonio})

    def post(self, request, id):
        testimonio = get_object_or_404(Testimonio, id=id)
        testimonio.delete()
        messages.success(request, "Testimonio eliminado correctamente.")
        return redirect('listar_testimonios')
