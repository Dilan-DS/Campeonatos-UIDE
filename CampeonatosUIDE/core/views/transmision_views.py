from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from core.models import Transmision, Campeonato, Partido  

# Mixin para permitir solo ADMIN o DELEGADO
class EsAdminODelegadoMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.rol in ['ADMIN', 'DELEGADO']

# Listar todas las transmisiones
class ListarTransmisionView(LoginRequiredMixin, View):
    def get(self, request):
        transmisiones = Transmision.objects.all()
        return render(request, 'transmision/listar_transmisiones.html', {
            'transmisiones': transmisiones
        })

# Crear transmisión
class CrearTransmisionView(LoginRequiredMixin, EsAdminODelegadoMixin, View):
    def get(self, request):
        campeonatos = Campeonato.objects.all()
        partidos = Partido.objects.all()
        return render(request, 'transmision/registrar_transmision.html', {
            'campeonatos': campeonatos,
            'partidos': partidos,
            'modo': 'crear',
            'transmision': {},
        })

    def post(self, request):
        campeonato_id = request.POST.get('campeonato')
        partido_id = request.POST.get('partido')
        enlace = request.POST.get('enlace')
        descripcion = request.POST.get('descripcion')
        activa = request.POST.get('activa') == 'on'

        if campeonato_id and partido_id and enlace:
            campeonato = get_object_or_404(Campeonato, id=campeonato_id)
            partido = get_object_or_404(Partido, id=partido_id)
            Transmision.objects.create(
                campeonato=campeonato,
                partido=partido,
                enlace=enlace,
                descripcion=descripcion,
                activa=activa
            )
            messages.success(request, "Transmisión registrada correctamente.")
            return redirect('listar_transmisiones')

        messages.error(request, "Todos los campos obligatorios deben ser completados.")
        campeonatos = Campeonato.objects.all()
        partidos = Partido.objects.all()
        transmision_data = {
            'campeonato': campeonato_id,
            'partido': partido_id,
            'enlace': enlace,
            'descripcion': descripcion,
            'activa': activa,
        }
        return render(request, 'transmision/registrar_transmision.html', {
            'campeonatos': campeonatos,
            'partidos': partidos,
            'modo': 'crear',
            'transmision': transmision_data,
        })

# Editar transmisión
class EditarTransmisionView(LoginRequiredMixin, EsAdminODelegadoMixin, View):
    def get(self, request, id):
        transmision = get_object_or_404(Transmision, id=id)
        campeonatos = Campeonato.objects.all()
        partidos = Partido.objects.all()
        return render(request, 'transmision/registrar_transmision.html', {
            'transmision': transmision,
            'campeonatos': campeonatos,
            'partidos': partidos,
            'modo': 'editar',
        })

    def post(self, request, id):
        transmision = get_object_or_404(Transmision, id=id)

        campeonato_id = request.POST.get('campeonato')
        partido_id = request.POST.get('partido')
        enlace = request.POST.get('enlace')
        descripcion = request.POST.get('descripcion')
        activa = request.POST.get('activa') == 'on'

        if not (campeonato_id and partido_id and enlace):
            messages.error(request, 'Todos los campos obligatorios deben estar llenos.')
            return redirect('editar_transmision', id=id)

        campeonato = get_object_or_404(Campeonato, id=campeonato_id)
        partido = get_object_or_404(Partido, id=partido_id)

        transmision.campeonato = campeonato
        transmision.partido = partido
        transmision.enlace = enlace
        transmision.descripcion = descripcion
        transmision.activa = activa

        try:
            transmision.clean()
            transmision.save()
            messages.success(request, 'Transmisión actualizada correctamente.')
            return redirect('listar_transmisiones')
        except Exception as e:
            messages.error(request, f'Error: {e}')
            return redirect('editar_transmision', id=id)

# Eliminar transmisión
class EliminarTransmisionView(LoginRequiredMixin, EsAdminODelegadoMixin, View):
    def get(self, request, id):
        transmision = get_object_or_404(Transmision, id=id)
        return render(request, 'transmision/registrar_transmision.html', {
            'transmision': transmision,
            'modo': 'eliminar',
        })

    def post(self, request, id):
        transmision = get_object_or_404(Transmision, id=id)
        transmision.delete()
        messages.success(request, 'Transmisión eliminada correctamente.')
        return redirect('listar_transmisiones')

# Ver detalles de una transmisión
class DetalleTransmisionView(LoginRequiredMixin, View):
    def get(self, request, id):
        transmision = get_object_or_404(Transmision, id=id)
        return render(request, 'transmision/registrar_transmision.html', {
            'transmision': transmision,
            'modo': 'detalle',
        })
