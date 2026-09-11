from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from core.forms import *

from core.models import (
    Usuario, Equipo, Jugador, Campeonato, Partido,
    # Arbitro y EstadisticaJugadorFutbol se usaban sin importar: las vistas de
    # gestión de árbitros y de exportación fallaban con NameError.
    Arbitro, EstadisticaJugadorFutbol, Pago,
)
from django.http import HttpResponse
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.db.models import Q
from datetime import datetime, timedelta
from core.permisos import es_admin


@login_required
@user_passes_test(es_admin)
# función para el dashboard del administrador
def admin_dashboard(request):
    # La plantilla se renderizaba sin contexto: las cuatro métricas mostraban
    # un guion y la tarjeta de fixture decía siempre "Aún no disponible".
    return render(request, 'dashboard/admin.html', {
        'kpi_usuarios': Usuario.objects.count(),
        'kpi_campeonatos': Campeonato.objects.filter(activo='SI').count(),
        'kpi_equipos': Equipo.objects.count(),
        'kpi_arbitros': Arbitro.objects.filter(estado=True).count(),
        'kpi_pagos_pendientes': Pago.objects.filter(estado='PENDIENTE').count(),
        'campeonato': (
            Campeonato.objects
            .filter(activo='SI')
            .order_by('-fecha_inicio')
            .first()
        ),
    })

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
            return redirect('vista_inicio')

        # Obtener todos los usuarios con rol JUGADOR
        jugadores_disponibles = Usuario.objects.filter(rol='JUGADOR').order_by('username')

        # Para cada jugador, verificar si ya está en un equipo
        jugadores_data = []
        for jugador_usuario in jugadores_disponibles:
            jugador_obj = Jugador.objects.filter(usuario=jugador_usuario).first()
            
            estado_inscripcion = ""
            ya_inscrito = False
            if jugador_obj:
                equipo_nombre = getattr(jugador_obj.equipo, 'nombre', 'Sin equipo')
                estado_inscripcion = f"Ya inscrito en: {equipo_nombre}"
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
            return redirect('vista_inicio')
        form = CrearUsuarioDelegadoForm()
        return render(request, 'delegado/registrar.html', {'form': form})

    def post(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
        form = CrearUsuarioDelegadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Delegado creado exitosamente.')
            return redirect('listar_delegados')
        messages.error(request, "Error al crear el delegado. Por favor, revisa los campos.")
        return render(request, 'delegado/registrar.html', {'form': form})

class GestionArbitroView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.rol == 'ADMIN'

    def get(self, request, id=None, action=None):
        arbitro_obj = None
        form = None
        modo = 'crear'

        if id:
            arbitro_obj = get_object_or_404(Arbitro, id=id)
            if action == 'editar':
                form = ArbitroForm(instance=arbitro_obj)
                modo = 'editar'
            elif action == 'eliminar':
                modo = 'eliminar'
            else: # Default to view if no action specified with ID
                modo = 'ver'
        else:
            form = CrearUsuarioArbitroForm()

        context = {
            'form': form,
            'arbitro': arbitro_obj,
            'modo': modo
        }
        return render(request, 'arbitro/registrar.html', context)

    def post(self, request, id=None, action=None):
        if action == 'eliminar':
            arbitro = get_object_or_404(Arbitro, id=id)
            arbitro.usuario.delete() # Also deletes the Arbitro object via CASCADE
            messages.success(request, "Árbitro eliminado correctamente.")
            return redirect('listar_arbitros')
        
        arbitro = None
        errores_json = None
        if id: # Edit existing
            arbitro = get_object_or_404(Arbitro, id=id)
            form = ArbitroForm(request.POST, instance=arbitro)
            if form.is_valid():
                form.save()
                messages.success(request, "Árbitro actualizado correctamente.")
                return redirect('listar_arbitros')
            else:
                errores_json = form.errors.get_json_data()
                messages.error(request, 'Revisa los errores del formulario.')
            modo = 'editar'
        else: # Create new
            form = CrearUsuarioArbitroForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Árbitro registrado correctamente.")
                return redirect('listar_arbitros')
            else:
                errores_json = form.errors.get_json_data()
                messages.error(request, 'Revisa los errores del formulario.')
            modo = 'crear'

        context = {
            'form': form,
            'arbitro': arbitro,
            'modo': modo,
            'errores_json': errores_json
        }
        return render(request, 'arbitro/registrar.html', context)


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
def exportar_estadisticas_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="estadisticas.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    data = [['Jugador', 'Campeonato', 'PJ', 'Goles', 'Amarillas', 'Rojas']]
    for stat in (EstadisticaJugadorFutbol.objects
                 .select_related('jugador__usuario', 'campeonato')
                 .order_by('-goles', 'jugador__usuario__username')):
        data.append([
            str(stat.jugador), str(stat.campeonato), stat.partidos_jugados,
            stat.goles, stat.tarjetas_amarillas, stat.tarjetas_rojas,
        ])

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

    sheet.append(['Jugador', 'Campeonato', 'PJ', 'Goles', 'Amarillas', 'Rojas'])

    for stat in (EstadisticaJugadorFutbol.objects
                 .select_related('jugador__usuario', 'campeonato')
                 .order_by('-goles', 'jugador__usuario__username')):
        sheet.append([
            str(stat.jugador), str(stat.campeonato), stat.partidos_jugados,
            stat.goles, stat.tarjetas_amarillas, stat.tarjetas_rojas,
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="estadisticas.xlsx"'
    workbook.save(response)
    return response


