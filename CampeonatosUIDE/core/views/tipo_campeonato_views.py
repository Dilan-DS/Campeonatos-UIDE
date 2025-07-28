from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib import messages
from core.models import TipoCampeonato
from core.forms import TipoCampeonatoForm

# Decoradores para las vistas basadas en clases
admin_required = [login_required, user_passes_test(lambda u: u.rol == 'ADMIN')]

@method_decorator(admin_required, name='dispatch')
class ListaTiposCampeonatoView(View):
    def get(self, request):
        tipos = TipoCampeonato.objects.all()
        return render(request, 'tipo_campeonato/listar_tipos.html', {'tipos': tipos})

@method_decorator(admin_required, name='dispatch')
class RegistrarTipoCampeonatoView(View):
    def get(self, request):
        form = TipoCampeonatoForm()
        return render(request, 'tipo_campeonato/registrar_tipo_campeonato.html', {
            'form': form,
            'modo': 'crear'  # IMPORTANTE: para el template
        })

    def post(self, request):
        form = TipoCampeonatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de campeonato registrado correctamente.')
            return redirect('listar_tipos_campeonato')
        return render(request, 'tipo_campeonato/registrar_tipo_campeonato.html', {
            'form': form,
            'modo': 'crear'  # IMPORTANTE: para el template
        })

@method_decorator(admin_required, name='dispatch')
class EditarTipoCampeonatoView(View):
    def get(self, request, id):
        tipo = get_object_or_404(TipoCampeonato, id=id)
        form = TipoCampeonatoForm(instance=tipo)
        return render(request, 'tipo_campeonato/registrar_tipo_campeonato.html', {
            'form': form,
            'tipo': tipo,
            'modo': 'editar'  # IMPORTANTE: para el template
        })

    def post(self, request, id):
        tipo = get_object_or_404(TipoCampeonato, id=id)
        form = TipoCampeonatoForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de campeonato actualizado correctamente.')
            return redirect('listar_tipos_campeonato')
        return render(request, 'tipo_campeonato/registrar_tipo_campeonato.html', {
            'form': form,
            'tipo': tipo,
            'modo': 'editar'  # IMPORTANTE: para el template
        })

@method_decorator(admin_required, name='dispatch')
class EliminarTipoCampeonatoView(View):
    def get(self, request, id):
        tipo = get_object_or_404(TipoCampeonato, id=id)
        return render(request, 'tipo_campeonato/registrar_tipo_campeonato.html', {
            'tipo': tipo,
            'modo': 'eliminar'  # IMPORTANTE: para el template
        })

    def post(self, request, id):
        tipo = get_object_or_404(TipoCampeonato, id=id)
        tipo.delete()
        messages.success(request, 'Tipo de campeonato eliminado correctamente.')
        return redirect('listar_tipos_campeonato')
