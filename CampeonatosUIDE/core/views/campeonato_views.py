from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from core.models import Campeonato
from core.forms import CampeonatoForm


class ListarCampeonatos(View):
    def get(self, request):
        campeonatos = Campeonato.objects.all().order_by('-fecha_inicio')
        return render(request, 'campeonato/listar.html', {
            'campeonatos': campeonatos
        })

class CrearCampeonato(View):
    def get(self, request):
        form = CampeonatoForm()
        return render(request, 'campeonato/crear.html', {'form': form, 'modo': 'crear'})

    def post(self, request):
        form = CampeonatoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campeonato creado correctamente')
            return redirect(reverse_lazy('listar_campeonatos'))
        else:
            return render(request, 'campeonato/crear.html', {'form': form, 'modo': 'crear'})

class EditarCampeonato(View):
    def get(self, request, id):
        campeonato = get_object_or_404(Campeonato, id=id)
        form = CampeonatoForm(instance=campeonato)
        return render(request, 'campeonato/crear.html', {
            'form': form,
            'campeonato': campeonato,
            'modo': 'editar'
        })

    def post(self, request, id):
        campeonato = get_object_or_404(Campeonato, id=id)
        form = CampeonatoForm(request.POST, request.FILES, instance=campeonato)

        if form.is_valid():
            cleaned = form.cleaned_data
            campeonato.nombre = cleaned.get('nombre', campeonato.nombre)
            campeonato.tipo_campeonato = cleaned.get('tipo_campeonato', campeonato.tipo_campeonato)
            campeonato.descripcion = cleaned.get('descripcion', campeonato.descripcion)
            campeonato.fecha_inicio = cleaned.get('fecha_inicio', campeonato.fecha_inicio)
            campeonato.fecha_fin = cleaned.get('fecha_fin', campeonato.fecha_fin)
            campeonato.estado = cleaned.get('estado', campeonato.estado)
            campeonato.deporte = cleaned.get('deporte', campeonato.deporte)
            campeonato.delegado = cleaned.get('delegado', campeonato.delegado)
            campeonato.dias_partido = cleaned.get('dias_partido', campeonato.dias_partido)
            campeonato.max_jugadores_por_equipo = cleaned.get('max_jugadores_por_equipo', campeonato.max_jugadores_por_equipo)
            campeonato.precio_inscripcion = cleaned.get('precio_inscripcion', campeonato.precio_inscripcion)
            campeonato.codigo_qr = cleaned.get('codigo_qr', campeonato.codigo_qr)
            campeonato.activo = cleaned.get('activo', campeonato.activo)
            campeonato.es_publico = cleaned.get('es_publico', campeonato.es_publico)

            if request.FILES.get('reglamento'):
                campeonato.reglamento = request.FILES['reglamento']

            campeonato.save()
            messages.success(request, 'Campeonato actualizado correctamente')
            return redirect(reverse_lazy('listar_campeonatos'))
        else:
            return render(request, 'campeonato/crear.html', {
                'form': form,
                'campeonato': campeonato
            })


class DetalleCampeonato(View):
    def get(self, request, id):
        campeonato = get_object_or_404(Campeonato, id=id)
        return render(request, 'campeonato/crear.html', {'campeonato': campeonato, 'modo': 'detalle'})

class FixtureCampeonato(View):
    def get(self, request, id):
        campeonato = get_object_or_404(Campeonato, id=id)
        return render(request, 'campeonato/fixture.html', {'campeonato': campeonato})

class CampeonatosPublicos(View):
    def get(self, request):
        campeonatos = Campeonato.objects.filter(activo=True)
        return render(request, 'campeonato/campeonatos_publicos.html', {
            'campeonatos': campeonatos
        })

def campeonatos_publicos(request):
    campeonatos = Campeonato.objects.filter(activo=True)
    return render(request, 'campeonato/campeonatos_publicos.html', {
        'campeonatos': campeonatos
    })

class EliminarCampeonato(View):
    def get(self, request, id):
        campeonato = get_object_or_404(Campeonato, id=id)
        return render(request, 'campeonato/crear.html', {
            'campeonato': campeonato,
            'modo': 'eliminar'
        })

    def post(self, request, id):
        campeonato = get_object_or_404(Campeonato, id=id)
        campeonato.delete()
        messages.success(request, 'Campeonato eliminado correctamente')
        return redirect(reverse_lazy('listar_campeonatos'))
