from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from core.utils.tabla_posiciones import calcular_tabla_posiciones
from core.models import Campeonato, Equipo, Partido
from core.forms import CampeonatoForm
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from core.utils.generar_fixture_liga import generar_fixture_liga
from core.utils.generar_fixture_eliminatoria import generar_fixture_eliminatoria
from core.utils.generar_fixture_fase_grupos import generar_fixture_fase_grupos


class EsAdminODelegadoMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.rol in ['ADMIN', 'DELEGADO']

def es_admin_o_delegado(user):
    return user.rol in ['ADMIN', 'DELEGADO']

import io
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.http import HttpResponse
import pandas as pd


# Clase para listar todos los campeonatos ordenados por fecha de inicio descendente
class ListarCampeonatos(LoginRequiredMixin, View):
    # Método GET para mostrar la lista de campeonatos
    def get(self, request):
        # Obtiene todos los campeonatos ordenados por fecha de inicio descendente
        campeonatos = Campeonato.objects.all().order_by('-fecha_inicio')
        # Renderiza el template con la lista de campeonatos
        return render(request, 'campeonato/listar.html', {
            'campeonatos': campeonatos
        })


# Clase para crear un nuevo campeonato
class CrearCampeonato(LoginRequiredMixin, EsAdminODelegadoMixin, View):
    # Método GET que muestra un formulario vacío para crear campeonato
    def get(self, request):
        # Instancia vacía del formulario CampeonatoForm
        form = CampeonatoForm()
        # Renderiza el template con el formulario y modo crear
        return render(request, 'campeonato/crear.html', {'form': form, 'modo': 'crear'})

    # Método POST que procesa el formulario enviado para crear campeonato
    def post(self, request):
        form = CampeonatoForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
            messages.success(request, "Campeonato creado correctamente.")
            return redirect("listar_campeonatos")
        else:
            print("CampeonatoForm errors:", form.errors)
            messages.error(request, "Revisa los campos del formulario.")
            return render(request, 'campeonato/crear.html', {'form': form, 'modo': 'crear'})


# Clase para editar un campeonato existente
class EditarCampeonato(LoginRequiredMixin, EsAdminODelegadoMixin, View):
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
            # Guarda los cambios en la base de datos
            form.save()
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
class DetalleCampeonato(LoginRequiredMixin, View):
    # Método GET que muestra información del campeonato en modo detalle
    def get(self, request, id):
        # Obtiene el campeonato o 404
        campeonato = get_object_or_404(Campeonato, id=id)
        # Renderiza el template con modo detalle
        return render(request, 'campeonato/crear.html', {'campeonato': campeonato, 'modo': 'detalle'})


# Clase para mostrar el fixture (calendario de partidos) de un campeonato
class FixtureCampeonato(LoginRequiredMixin, View):
    def get(self, request, id, deporte_id=None):
        campeonato = get_object_or_404(Campeonato, id=id)
        genero = request.GET.get('genero', 'masculino').lower()
        if genero not in ('masculino', 'femenino'):
            genero = 'masculino'
        
        return render(request, 'feachure/calendar.html', {
            'campeonato': campeonato,
            'partidos': Partido.objects.filter(campeonato=campeonato, equipo_local__genero=genero, equipo_visitante__genero=genero).order_by('fecha','hora'),
            'genero_seleccionado': genero,
            'campeonato_sin_fixture': not Partido.objects.filter(campeonato=campeonato).exists(),
        })


# Clase para mostrar campeonatos públicos y activos
class CampeonatosPublicos(View):
    # Método GET que obtiene solo campeonatos activos
    def get(self, request):
        campeonatos = Campeonato.objects.filter(activo='SI').order_by('-fecha_inicio')
        return render(request, 'campeonato/campeonatos_publicos.html', {'campeonatos': campeonatos})


# Función alternativa para listar campeonatos públicos activos
def campeonatos_publicos(request):
    campeonatos = Campeonato.objects.filter(activo='SI').order_by('-fecha_inicio')
    return render(request, 'campeonato/campeonatos_publicos.html', {'campeonatos': campeonatos})


# Clase para eliminar un campeonato
class EliminarCampeonato(LoginRequiredMixin, EsAdminODelegadoMixin, View):
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


class TablaPosiciones(LoginRequiredMixin, View):
    def get(self, request, campeonato_id):
        campeonato = get_object_or_404(Campeonato, id=campeonato_id)
        tabla_ordenada = calcular_tabla_posiciones(campeonato)

        context = {
            'campeonato': campeonato,
            'tabla': tabla_ordenada
        }
        return render(request, 'campeonato/tabla_posiciones.html', context)


class GenerarFixtureCampeonato(LoginRequiredMixin, EsAdminODelegadoMixin, View):
    def post(self, request, campeonato_id):
        campeonato = get_object_or_404(Campeonato, id=campeonato_id)

        if Equipo.objects.filter(campeonato=campeonato, aprobado=True).count() < 2:
            messages.error(request, "Se necesitan al menos 2 equipos aprobados para generar el fixture.")
            return redirect('fixture_campeonato_detalle', campeonato_id=campeonato.id)

        Partido.objects.filter(campeonato=campeonato).delete()

        tipo = campeonato.tipo_campeonato
        creados = 0
        if tipo == 'LIGA':
            creados = generar_fixture_liga(campeonato.id) or 0
        elif tipo == 'FASE_GRUPOS':
            creados = generar_fixture_fase_grupos(campeonato.id) or 0
        else:
            creados = generar_fixture_eliminatoria(campeonato.id) or 0

        

        if creados > 0:
            campeonato.fixture_generado = True
            if campeonato.estado == 'INSCRIPCION':
                campeonato.estado = 'EN_CURSO'
            campeonato.save(update_fields=['fixture_generado', 'estado'])
            messages.success(request, "Fixture generado.")
        else:
            messages.warning(request, "No se generaron partidos (verifica que haya al menos 2 equipos por género).")

        return redirect('fixture_campeonato_detalle', campeonato_id=campeonato.id)


@login_required
@user_passes_test(es_admin_o_delegado)
def export_tabla_posiciones_pdf(request, campeonato_id):
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)
    equipos = Equipo.objects.filter(campeonato=campeonato, aprobado=True)

    tabla = []
    for equipo in equipos:
        pj = 0  # Partidos Jugados
        pg = 0  # Partidos Ganados
        pe = 0  # Partidos Empatados
        pp = 0  # Partidos Perdidos
        gf = 0  # Goles a Favor
        gc = 0  # Goles en Contra
        puntos = 0

        # Partidos como local
        partidos_local = Partido.objects.filter(
            campeonato=campeonato,
            equipo_local=equipo,
            estado='FINALIZADO'
        )
        for p in partidos_local:
            pj += 1
            gf += p.resultado_local
            gc += p.resultado_visitante
            if p.resultado_local > p.resultado_visitante:
                pg += 1
                puntos += 3
            elif p.resultado_local == p.resultado_visitante:
                pe += 1
                puntos += 1
            else:
                pp += 1

        # Partidos como visitante
        partidos_visitante = Partido.objects.filter(
            campeonato=campeonato,
            equipo_visitante=equipo,
            estado='FINALIZADO'
        )
        for p in partidos_visitante:
            pj += 1
            gf += p.resultado_visitante
            gc += p.resultado_local
            if p.resultado_visitante > p.resultado_local:
                pg += 1
                puntos += 3
            elif p.resultado_visitante == p.resultado_local:
                pe += 1
                puntos += 1
            else:
                pp += 1
        
        gd = gf - gc # Diferencia de Goles

        tabla.append({
            'equipo': equipo,
            'pj': pj,
            'pg': pg,
            'pe': pe,
            'pp': pp,
            'gf': gf,
            'gc': gc,
            'gd': gd,
            'puntos': puntos
        })
    
    tabla_ordenada = sorted(tabla, key=lambda x: (x['puntos'], x['gd'], x['gf']), reverse=True)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['h2'],
        alignment=1, # CENTER
        spaceAfter=14
    )

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=1, # CENTER
        spaceAfter=6
    )

    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        alignment=1, # CENTER
        spaceAfter=2
    )

    elements = []
    elements.append(Paragraph(f"Tabla de Posiciones - {campeonato.nombre}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    data = [
        [
            Paragraph("Posición", header_style),
            Paragraph("Equipo", header_style),
            Paragraph("PJ", header_style),
            Paragraph("PG", header_style),
            Paragraph("PE", header_style),
            Paragraph("PP", header_style),
            Paragraph("GF", header_style),
            Paragraph("GC", header_style),
            Paragraph("GD", header_style),
            Paragraph("Puntos", header_style)
        ]
    ]
    for i, row in enumerate(tabla_ordenada):
        data.append([
            Paragraph(str(i + 1), content_style),
            Paragraph(row['equipo'].nombre, content_style),
            Paragraph(str(row['pj']), content_style),
            Paragraph(str(row['pg']), content_style),
            Paragraph(str(row['pe']), content_style),
            Paragraph(str(row['pp']), content_style),
            Paragraph(str(row['gf']), content_style),
            Paragraph(str(row['gc']), content_style),
            Paragraph(str(row['gd']), content_style),
            Paragraph(str(row['puntos']), content_style)
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


@login_required
@user_passes_test(es_admin_o_delegado)
def export_tabla_posiciones_excel(request, campeonato_id):
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)
    equipos = Equipo.objects.filter(campeonato=campeonato, aprobado=True)

    tabla = []
    for equipo in equipos:
        pj = 0  # Partidos Jugados
        pg = 0  # Partidos Ganados
        pe = 0  # Partidos Empatados
        pp = 0  # Partidos Perdidos
        gf = 0  # Goles a Favor
        gc = 0  # Goles en Contra
        puntos = 0

        # Partidos como local
        partidos_local = Partido.objects.filter(
            campeonato=campeonato,
            equipo_local=equipo,
            estado='FINALIZADO'
        )
        for p in partidos_local:
            pj += 1
            gf += p.resultado_local
            gc += p.resultado_visitante
            if p.resultado_local > p.resultado_visitante:
                pg += 1
                puntos += 3
            elif p.resultado_local == p.resultado_visitante:
                pe += 1
                puntos += 1
            else:
                pp += 1

        # Partidos como visitante
        partidos_visitante = Partido.objects.filter(
            campeonato=campeonato,
            equipo_visitante=equipo,
            estado='FINALIZADO'
        )
        for p in partidos_visitante:
            pj += 1
            gf += p.resultado_visitante
            gc += p.resultado_local
            if p.resultado_visitante > p.resultado_local:
                pg += 1
                puntos += 3
            elif p.resultado_visitante == p.resultado_local:
                pe += 1
                puntos += 1
            else:
                pp += 1
        
        gd = gf - gc # Diferencia de Goles

        tabla.append({
            'equipo': equipo,
            'pj': pj,
            'pg': pg,
            'pe': pe,
            'pp': pp,
            'gf': gf,
            'gc': gc,
            'gd': gd,
            'puntos': puntos
        })
    
    tabla_ordenada = sorted(tabla, key=lambda x: (x['puntos'], x['gd'], x['gf']), reverse=True)

    data = []
    for i, row in enumerate(tabla_ordenada):
        data.append({
            'Posición': i + 1,
            'Equipo': row['equipo'].nombre,
            'PJ': row['pj'],
            'PG': row['pg'],
            'PE': row['pe'],
            'PP': row['pp'],
            'GF': row['gf'],
            'GC': row['gc'],
            'GD': row['gd'],
            'Puntos': row['puntos'],
        })

    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tabla de Posiciones')
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=tabla_posiciones_{campeonato.nombre.replace(" ", "_")}.xlsx'
    return response
