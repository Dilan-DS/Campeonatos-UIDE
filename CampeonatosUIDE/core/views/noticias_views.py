from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Noticia
from core.forms import NoticiaForm

class ListarNoticias(View):
    def get(self, request):
        noticias = Noticia.objects.all().order_by('-fecha_publicacion')
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

class EliminarNoticia(View):
    def get(self, request, id):
        noticia = get_object_or_404(Noticia, id=id)
        return render(request, 'noticia/form.html', {'noticia': noticia})

    def post(self, request, id):
        noticia = get_object_or_404(Noticia, id=id)
        noticia.delete()
        messages.success(request, "Noticia eliminada correctamente.")
        return redirect('listar_noticias')
