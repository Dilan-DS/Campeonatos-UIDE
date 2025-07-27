from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from core.models import Arbitro
from core.forms import ArbitroForm

# ========================
# CLASES BASADAS EN VISTAS (CBV) - ÁRBITROS
# ========================

class listar_arbitros(View):
    def get(self, request):
        arbitros = Arbitro.objects.all()
        return render(request, 'arbitro/listar.html', {
            'arbitros': arbitros
        })


class registrar_arbitro(View):
    def get(self, request):
        form = ArbitroForm()
        return render(request, 'arbitro/registrar.html', {
            'form': form,
            'modo': 'crear'
        })

    def post(self, request):
        form = ArbitroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Árbitro registrado correctamente')
            return redirect('listar_arbitros')
        return render(request, 'arbitro/registrar.html', {
            'form': form,
            'modo': 'crear'
        })


class editar_arbitro(View):
    def get(self, request, id):
        arbitro = get_object_or_404(Arbitro, id=id)
        form = ArbitroForm(instance=arbitro)
        return render(request, 'arbitro/registrar.html', {
            'form': form,
            'arbitro': arbitro,
            'modo': 'editar'
        })

    def post(self, request, id):
        arbitro = get_object_or_404(Arbitro, id=id)
        form = ArbitroForm(request.POST)
        if form.is_valid():
            # Actualización manual de campos
            arbitro.nombre = form.cleaned_data['nombre']
            arbitro.apellido = form.cleaned_data['apellido']
            arbitro.experiencia = form.cleaned_data['experiencia']
            arbitro.contacto = form.cleaned_data['contacto']
            arbitro.estado = form.cleaned_data['estado']
            arbitro.save()
            arbitro.deportes.set(form.cleaned_data['deportes'])

            messages.success(request, 'Árbitro actualizado correctamente')
            return redirect('listar_arbitros')

        return render(request, 'arbitro/registrar.html', {
            'form': form,
            'arbitro': arbitro,
            'modo': 'editar'
        })


class detalle_arbitro(View):
    def get(self, request, id):
        arbitro = get_object_or_404(Arbitro, id=id)
        return render(request, 'arbitro/registrar.html', {
            'arbitro': arbitro,
            'modo': 'detalle'
        })


class eliminar_arbitro(View):
    def get(self, request, id):
        arbitro = get_object_or_404(Arbitro, id=id)
        return render(request, 'arbitro/registrar.html', {'modo': 'eliminar', 'arbitro': arbitro})

    def post(self, request, id):
        arbitro = get_object_or_404(Arbitro, id=id)
        arbitro.delete()
        messages.success(request, 'Árbitro eliminado correctamente')
        return redirect('listar_arbitros')