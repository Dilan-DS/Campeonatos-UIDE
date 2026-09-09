from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Noticia
from core.forms import NoticiaForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from core.views.campeonato_views import es_admin_o_delegado

class ListarNoticias(View):
    def get(self, request):
        noticias = Noticia.objects.all().order_by('-creado_en')
        return render(request, 'noticia/listar.html', {'noticias': noticias})

class RegistrarNoticia(View):
    def get(self, request):
        form = NoticiaForm()
        return render(request, 'noticia/form.html', {'form': form, 'modo': 'crear'})

    def post(self, request):
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Noticia registrada correctamente.")
            return redirect('listar_noticias')
        return render(request, 'noticia/form.html', {'form': form, 'modo': 'crear'})

class EditarNoticia(View):
    def get(self, request, id):
        noticia = get_object_or_404(Noticia, id=id)
        form = NoticiaForm(instance=noticia)
        return render(request, 'noticia/form.html', {'form': form, 'modo': 'editar', 'noticia': noticia})

    def post(self, request, id):
        noticia = get_object_or_404(Noticia, id=id)
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            form.save()
            messages.success(request, "Noticia actualizada correctamente.")
            return redirect('listar_noticias')
        return render(request, 'noticia/form.html', {'form': form, 'modo': 'editar', 'noticia': noticia})

class EliminarNoticia(LoginRequiredMixin, UserPassesTestMixin, View):
    """GET: muestra confirmación | POST: elimina.
       Solo ADMIN puede eliminar.
    """
    def test_func(self):
        return getattr(self.request.user, "rol", "") == "ADMIN"

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para eliminar noticias.")
        return redirect("listar_noticias")

    def get(self, request, id):
        noticia = get_object_or_404(Noticia, id=id)
        return render(request, "noticia/eliminar.html", {"noticia": noticia})

    def post(self, request, id):
        noticia = get_object_or_404(Noticia, id=id)
        titulo = noticia.titulo
        noticia.delete()
        messages.success(request, f'La noticia “{titulo}” fue eliminada correctamente.')
        return redirect("listar_noticias")
