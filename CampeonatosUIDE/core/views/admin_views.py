from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from core.forms import *
from core.models import Usuario, Equipo, Jugador, Campeonato, Partido
from django.http import HttpResponse
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.db.models import Q
from datetime import datetime, timedelta


def es_admin(user):
    # Verifica si el usuario es un administrador
    return user.rol == 'ADMIN'

@login_required
@user_passes_test(es_admin)
# función para el dashboard del administrador
def admin_dashboard(request):
    # Renderiza la plantilla 'admin.html' para el dashboard del administrador
    return render(request, 'dashboard/admin.html')

@login_required
@user_passes_test(es_admin)
def listar_usuarios(request):
    query = request.GET.get('buscar', '')
    if query:
        usuarios = Usuario.objects.filter(
            Q(username__icontains=query) | Q(cedula__icontains=query)
        )
    else:
        usuarios = Usuario.objects.all()

    return render(request, 'usuario/admin_listar.html', {
        'usuarios': usuarios,
        'query': query
    })

class ListarJugadoresAdminView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('inicio')

        # Obtener todos los usuarios con rol JUGADOR
        jugadores_disponibles = Usuario.objects.filter(rol='JUGADOR').order_by('username')

        # Para cada jugador, verificar si ya está en un equipo
        jugadores_data = []
        for jugador_usuario in jugadores_disponibles:
            jugador_obj = Jugador.objects.filter(usuario=jugador_usuario).first()
            
            estado_inscripcion = ""
            ya_inscrito = False
            if jugador_obj:
                estado_inscripcion = f"Ya inscrito en: {jugador_obj.equipo.nombre}"
                ya_inscrito = True
            
            jugadores_data.append({
                'usuario': jugador_usuario,
                'ya_inscrito': ya_inscrito,
                'estado_inscripcion': estado_inscripcion,
            })
        
        context = {
            'jugadores_data': jugadores_data,
            'is_admin_view': True, # Para controlar la visibilidad de botones en el template
        }
        return render(request, 'jugador/listar_jugadores.html', context)

@login_required
@user_passes_test(es_admin)
# Vista para crear un nuevo usuario administrador
def crear_usuario_admin(request):
    # Verifica si la solicitud es POST (envío de formulario)
    if request.method == 'POST':
        # Crea una instancia del formulario CrearUsuarioAdminForm con los datos enviados
        form = CrearUsuarioAdminForm(request.POST)
        # Verifica si el formulario es válido
        if form.is_valid():
            # Si el formulario es válido, guarda el nuevo usuario administrador
            user = form.save()
            # Asigna el rol de 'ADMIN' al nuevo usuario
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('admin_dashboard')
    else:
        # Si la solicitud no es POST, crea un formulario vacío
        form = CrearUsuarioAdminForm()
    # Renderiza la plantilla 'crear_usuario_admin.html' con el formulario
    return render(request, 'admin_panel/registro_usuario.html', {'form': form})

class RegistrarDelegadoAdminView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('inicio')
        form = CrearUsuarioDelegadoForm()
        return render(request, 'delegado/registrar.html', {'form': form})

    def post(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('inicio')
        form = CrearUsuarioDelegadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Delegado creado exitosamente.')
            return redirect('listar_delegados')
        messages.error(request, "Error al crear el delegado. Por favor, revisa los campos.")
        return render(request, 'delegado/registrar.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def registrar_arbitro(request):
    if request.method == 'POST':
        form = CrearUsuarioArbitroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Árbitro creado exitosamente.')
            return redirect('admin_dashboard')
    else:
        form = CrearUsuarioArbitroForm()
    return render(request, 'arbitro/registrar.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('listar_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuario/editar_admin.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, "Usuario eliminado correctamente.")
        return redirect('listar_usuarios')
    return render(request, 'usuario/confirmar_eliminacion_admin.html', {'usuario': usuario})


@login_required
@user_passes_test(es_admin)
def generar_calendario(request, campeonato_id):
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)
    return render(request, 'campeonato/generar_calendario.html', {'campeonato': campeonato})

@login_required
@user_passes_test(es_admin)
def exportar_estadisticas_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="estadisticas.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    data = [['Jugador', 'Goles', 'Asistencias']]
    for stat in EstadisticaJugadorFutbol.objects.all():
        data.append([str(stat.jugador), stat.goles, stat.asistencias])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(table)

    doc.build(elements)
    return response

@login_required
@user_passes_test(es_admin)
def exportar_estadisticas_excel(request):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Estadísticas de Fútbol"

    sheet.append(['Jugador', 'Goles', 'Asistencias'])

    for stat in EstadisticaJugadorFutbol.objects.all():
        sheet.append([str(stat.jugador), stat.goles, stat.asistencias])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="estadisticas.xlsx"'
    workbook.save(response)
    return response
