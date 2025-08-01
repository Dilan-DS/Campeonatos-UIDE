from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Testimonio
from core.forms import TestimonioForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from core.views.campeonato_views import es_admin_o_delegado

class ListarTestimonios(View):
    def get(self, request):
        testimonios = Testimonio.objects.all().order_by('-fecha')
        return render(request, 'testimonio/listar.html', {'testimonios': testimonios})

class RegistrarTestimonio(View):
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

class EditarTestimonio(View):
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

class EliminarTestimonio(View):
    def get(self, request, id):
        testimonio = get_object_or_404(Testimonio, id=id)
        return render(request, 'testimonio/form.html', {'testimonio': testimonio})

    def post(self, request, id):
        testimonio = get_object_or_404(Testimonio, id=id)
        testimonio.delete()
        messages.success(request, "Testimonio eliminado correctamente.")
        return redirect('listar_testimonios')
