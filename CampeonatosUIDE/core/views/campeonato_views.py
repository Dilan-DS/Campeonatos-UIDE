# Importa funciones para renderizar templates, redireccionar y obtener objeto o error 404
from django.shortcuts import render, redirect, get_object_or_404
# Importa el sistema de mensajes para mostrar alertas al usuario
from django.contrib import messages
# Importa reverse_lazy para usar nombres de rutas en redirecciones
from django.urls import reverse_lazy
# Importa la clase base para vistas basadas en clases (CBV)
from django.views import View
# Importa el modelo Campeonato de la aplicación core
from core.models import Campeonato
# Importa el formulario CampeonatoForm para manipular datos de campeonatos
from core.forms import CampeonatoForm


# Clase para listar todos los campeonatos ordenados por fecha de inicio descendente
class ListarCampeonatos(View):
    # Método GET para mostrar la lista de campeonatos
    def get(self, request):
        # Obtiene todos los campeonatos ordenados por fecha de inicio descendente
        campeonatos = Campeonato.objects.all().order_by('-fecha_inicio')
        # Renderiza el template con la lista de campeonatos
        return render(request, 'campeonato/listar.html', {
            'campeonatos': campeonatos
        })


# Clase para crear un nuevo campeonato
class CrearCampeonato(View):
    # Método GET que muestra un formulario vacío para crear campeonato
    def get(self, request):
        # Instancia vacía del formulario CampeonatoForm
        form = CampeonatoForm()
        # Renderiza el template con el formulario y modo crear
        return render(request, 'campeonato/crear.html', {'form': form, 'modo': 'crear'})

    # Método POST que procesa el formulario enviado para crear campeonato
    def post(self, request):
        # Instancia del formulario con datos enviados y archivos (como reglamento)
        form = CampeonatoForm(request.POST, request.FILES)
        # Valida el formulario
        if form.is_valid():
            # Guarda el nuevo campeonato en la base de datos
            form.save()
            # Mensaje de éxito al usuario
            messages.success(request, 'Campeonato creado correctamente')
            # Redirige a la lista de campeonatos usando reverse_lazy para la ruta nombrada
            return redirect(reverse_lazy('listar_campeonatos'))
        else:
            # Si no es válido, vuelve a mostrar el formulario con errores
            return render(request, 'campeonato/crear.html', {'form': form, 'modo': 'crear'})


# Clase para editar un campeonato existente
class EditarCampeonato(View):
    # Método GET que muestra formulario con datos actuales para editar
    def get(self, request, id):
        # Obtiene el campeonato por su id o lanza 404 si no existe
        campeonato = get_object_or_404(Campeonato, id=id)
        # Instancia del formulario rellenado con datos del campeonato
        form = CampeonatoForm(instance=campeonato)
        # Renderiza el template con formulario, campeonato y modo editar
        return render(request, 'campeonato/crear.html', {
            'form': form,
            'campeonato': campeonato,
            'modo': 'editar'
        })

    # Método POST que procesa el formulario para actualizar el campeonato
    def post(self, request, id):
        # Obtiene el campeonato o 404
        campeonato = get_object_or_404(Campeonato, id=id)
        # Instancia del formulario con datos enviados, archivos y la instancia a actualizar
        form = CampeonatoForm(request.POST, request.FILES, instance=campeonato)

        # Valida el formulario
        if form.is_valid():
            # Obtiene datos limpios para actualizar manualmente
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

            # Si se subió un nuevo archivo reglamento, actualiza el campo
            if request.FILES.get('reglamento'):
                campeonato.reglamento = request.FILES['reglamento']

            # Guarda los cambios en la base de datos
            campeonato.save()
            # Mensaje de éxito
            messages.success(request, 'Campeonato actualizado correctamente')
            # Redirige a la lista de campeonatos
            return redirect(reverse_lazy('listar_campeonatos'))
        else:
            # Si no válido, vuelve a mostrar el formulario con errores y datos actuales
            return render(request, 'campeonato/crear.html', {
                'form': form,
                'campeonato': campeonato
            })


# Clase para mostrar detalles de un campeonato
class DetalleCampeonato(View):
    # Método GET que muestra información del campeonato en modo detalle
    def get(self, request, id):
        # Obtiene el campeonato o 404
        campeonato = get_object_or_404(Campeonato, id=id)
        # Renderiza el template con modo detalle
        return render(request, 'campeonato/crear.html', {'campeonato': campeonato, 'modo': 'detalle'})


# Clase para mostrar el fixture (calendario de partidos) de un campeonato
class FixtureCampeonato(View):
    # Método GET para mostrar el fixture
    def get(self, request, id):
        # Obtiene el campeonato o 404
        campeonato = get_object_or_404(Campeonato, id=id)
        # Renderiza el template específico para fixture
        return render(request, 'campeonato/fixture.html', {'campeonato': campeonato})


# Clase para mostrar campeonatos públicos y activos
class CampeonatosPublicos(View):
    # Método GET que obtiene solo campeonatos activos
    def get(self, request):
        campeonatos = Campeonato.objects.filter(activo=True)
        # Renderiza la lista de campeonatos públicos
        return render(request, 'campeonato/campeonatos_publicos.html', {
            'campeonatos': campeonatos
        })


# Función alternativa para listar campeonatos públicos activos
def campeonatos_publicos(request):
    campeonatos = Campeonato.objects.filter(activo=True)
    # Renderiza la misma plantilla que la clase anterior
    return render(request, 'campeonato/campeonatos_publicos.html', {
        'campeonatos': campeonatos
    })


# Clase para eliminar un campeonato
class EliminarCampeonato(View):
    # Método GET que muestra confirmación para eliminar
    def get(self, request, id):
        # Obtiene el campeonato o 404
        campeonato = get_object_or_404(Campeonato, id=id)
        # Renderiza el template en modo eliminar
        return render(request, 'campeonato/crear.html', {
            'campeonato': campeonato,
            'modo': 'eliminar'
        })

    # Método POST que elimina el campeonato después de confirmación
    def post(self, request, id):
        # Obtiene el campeonato o 404
        campeonato = get_object_or_404(Campeonato, id=id)
        # Elimina el objeto de la base de datos
        campeonato.delete()
        # Muestra mensaje de éxito
        messages.success(request, 'Campeonato eliminado correctamente')
        # Redirige a la lista de campeonatos
        return redirect(reverse_lazy('listar_campeonatos'))
