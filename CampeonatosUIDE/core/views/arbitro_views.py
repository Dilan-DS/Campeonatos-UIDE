# Importa funciones para renderizar templates, redireccionar y obtener objetos o error 404 si no existen
from django.shortcuts import render, redirect, get_object_or_404
# Importa la clase base para vistas basadas en clases (CBV)
from django.views import View
# Importa el sistema de mensajes para mostrar alertas al usuario
from django.contrib import messages
# Importa el modelo Arbitro de la aplicación core
from core.models import Arbitro, Partido
# Importa el formulario ArbitroForm para manipular datos de árbitros
from core.forms import ArbitroForm, CrearUsuarioArbitroForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# ========================
# CLASES BASADAS EN VISTAS (CBV) - ÁRBITROS
# ========================

# Clase para listar todos los árbitros
class listar_arbitros(View):
    # Método GET que maneja la solicitud de la página para mostrar árbitros
    def get(self, request):
        # Obtiene todos los objetos Arbitro de la base de datos
        arbitros = Arbitro.objects.all()
        # Renderiza el template 'arbitro/listar.html' enviando la lista de árbitros
        return render(request, 'arbitro/listar.html', {
            'arbitros': arbitros
        })


from core.views.campeonato_views import es_admin_o_delegado
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class GestionArbitroView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return es_admin_o_delegado(self.request.user)

    def get(self, request, id=None, action=None):
        arbitro = None
        form = None
        modo = 'crear' # Default mode

        if id:
            arbitro = get_object_or_404(Arbitro, id=id)
            if action == 'editar':
                form = ArbitroForm(instance=arbitro)
                modo = 'editar'
            elif action == 'eliminar':
                modo = 'eliminar'
            else: # Default to 'ver' if no action specified with ID
                modo = 'ver'
        else: # No ID, so it's a creation
            form = CrearUsuarioArbitroForm()

        context = {
            'form': form,
            'arbitro': arbitro,
            'modo': modo
        }
        return render(request, 'arbitro/registrar.html', context)

    def post(self, request, id=None, action=None):
        if action == 'eliminar':
            arbitro = get_object_or_404(Arbitro, id=id)
            arbitro.delete()
            messages.success(request, 'Árbitro eliminado correctamente.')
            return redirect('listar_arbitros')
        elif id: # Editing an existing referee
            arbitro = get_object_or_404(Arbitro, id=id)
            form = ArbitroForm(request.POST, instance=arbitro)
            if form.is_valid():
                form.save()
                messages.success(request, 'Árbitro actualizado correctamente.')
                return redirect('listar_arbitros')
            modo = 'editar' # Stay in edit mode if form is invalid
        else: # Creating a new referee
            form = CrearUsuarioArbitroForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Árbitro registrado correctamente.')
                return redirect('listar_arbitros')
            modo = 'crear' # Stay in create mode if form is invalid

        context = {
            'form': form,
            'arbitro': arbitro,
            'modo': modo
        }
        return render(request, 'arbitro/registrar.html', context)



@method_decorator(login_required, name='dispatch')
class HistorialArbitrosView(View):
    def get(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('inicio')  # Redirect to a safe page

        arbitros = Arbitro.objects.all()
        arbitros_con_partidos = []
        for arbitro in arbitros:
            partidos_arbitrados = Partido.objects.filter(arbitro=arbitro).order_by('-fecha', '-hora')
            arbitros_con_partidos.append({
                'arbitro': arbitro,
                'partidos': partidos_arbitrados
            })
        return render(request, 'arbitro/historial_arbitros.html', {'arbitros_con_partidos': arbitros_con_partidos})


@login_required
def mis_partidos_arbitro(request):
    try:
        arbitro = request.user.arbitro
        partidos = Partido.objects.filter(arbitro=arbitro).order_by('fecha', 'hora')
        return render(request, 'arbitro/mis_partidos.html', {'partidos': partidos})
    except Arbitro.DoesNotExist:
        messages.error(request, "No estás registrado como árbitro.")
        return redirect('vista_inicio')
