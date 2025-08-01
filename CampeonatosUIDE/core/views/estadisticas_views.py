from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
import io
from openpyxl import Workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import pandas as pd
from ..models import (
    EstadisticaJugadorFutbol, EstadisticaJugadorBasquet, EstadisticaJugadorAjedrez,
    EstadisticaJugadorEcuaboly, EstadisticaJugadorPingPong, EstadisticaJugadorTenis,
    EstadisticaJugadorVideojuegos, EstadisticaJugadorFutbolin, Jugador, Campeonato
)

def es_admin_o_delegado(user):
    return user.rol in ['ADMIN', 'DELEGADO']

# ========================
# ESTADÍSTICAS
# ========================

@login_required
def estadisticas_futbol(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        campeonato = get_object_or_404(Campeonato, id=campeonato_id)
        estadisticas = EstadisticaJugadorFutbol.objects.filter(campeonato=campeonato).order_by('-goles')
    else:
        estadisticas = EstadisticaJugadorFutbol.objects.all().order_by('-goles')
    
    campeonatos = Campeonato.objects.all()
    context = {
        'estadisticas': estadisticas,
        'campeonatos': campeonatos,
        'selected_campeonato_id': int(campeonato_id) if campeonato_id else None
    }
    return render(request, 'estadisticas/estadisticas_futbol.html', context)

@login_required
def estadisticas_basquet(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        campeonato = get_object_or_404(Campeonato, id=campeonato_id)
        estadisticas = EstadisticaJugadorBasquet.objects.filter(campeonato=campeonato).order_by('-canastas')
    else:
        estadisticas = EstadisticaJugadorBasquet.objects.all().order_by('-canastas')

    campeonatos = Campeonato.objects.all()
    context = {
        'estadisticas': estadisticas,
        'campeonatos': campeonatos,
        'selected_campeonato_id': int(campeonato_id) if campeonato_id else None
    }
    return render(request, 'estadisticas/estadisticas_basquet.html', context)

@login_required
def estadisticas_ecuaboly(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        campeonato = get_object_or_404(Campeonato, id=campeonato_id)
        estadisticas = EstadisticaJugadorEcuaboly.objects.filter(campeonato=campeonato).order_by('-sets_ganados')
    else:
        estadisticas = EstadisticaJugadorEcuaboly.objects.all().order_by('-sets_ganados')

    campeonatos = Campeonato.objects.all()
    context = {
        'estadisticas': estadisticas,
        'campeonatos': campeonatos,
        'selected_campeonato_id': int(campeonato_id) if campeonato_id else None
    }
    return render(request, 'estadisticas/estadisticas_ecuaboly.html', context)

@login_required
def estadisticas_ajedrez(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        campeonato = get_object_or_404(Campeonato, id=campeonato_id)
        estadisticas = EstadisticaJugadorAjedrez.objects.filter(campeonato=campeonato).order_by('-partidas_ganadas')
    else:
        estadisticas = EstadisticaJugadorAjedrez.objects.all().order_by('-partidas_ganadas')

    campeonatos = Campeonato.objects.all()
    context = {
        'estadisticas': estadisticas,
        'campeonatos': campeonatos,
        'selected_campeonato_id': int(campeonato_id) if campeonato_id else None
    }
    return render(request, 'estadisticas/estadisticas_ajedrez.html', context)

@login_required
def estadisticas_futbolin(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        campeonato = get_object_or_404(Campeonato, id=campeonato_id)
        estadisticas = EstadisticaJugadorFutbolin.objects.filter(campeonato=campeonato).order_by('-goles')
    else:
        estadisticas = EstadisticaJugadorFutbolin.objects.all().order_by('-goles')

    campeonatos = Campeonato.objects.all()
    context = {
        'estadisticas': estadisticas,
        'campeonatos': campeonatos,
        'selected_campeonato_id': int(campeonato_id) if campeonato_id else None
    }
    return render(request, 'estadisticas/estadisticas_futbolin.html', context)

@login_required
def estadisticas_pingpong(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        campeonato = get_object_or_404(Campeonato, id=campeonato_id)
        estadisticas = EstadisticaJugadorPingPong.objects.filter(campeonato=campeonato).order_by('-partidos_ganados')
    else:
        estadisticas = EstadisticaJugadorPingPong.objects.all().order_by('-partidos_ganados')

    campeonatos = Campeonato.objects.all()
    context = {
        'estadisticas': estadisticas,
        'campeonatos': campeonatos,
        'selected_campeonato_id': int(campeonato_id) if campeonato_id else None
    }
    return render(request, 'estadisticas/estadisticas_pingpong.html', context)

@login_required
def estadisticas_tenis(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        campeonato = get_object_or_404(Campeonato, id=campeonato_id)
        estadisticas = EstadisticaJugadorTenis.objects.filter(campeonato=campeonato).order_by('-sets_ganados')
    else:
        estadisticas = EstadisticaJugadorTenis.objects.all().order_by('-sets_ganados')

    campeonatos = Campeonato.objects.all()
    context = {
        'estadisticas': estadisticas,
        'campeonatos': campeonatos,
        'selected_campeonato_id': int(campeonato_id) if campeonato_id else None
    }
    return render(request, 'estadisticas/estadisticas_tenis.html', context)

@login_required
def estadisticas_videojuegos(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        campeonato = get_object_or_404(Campeonato, id=campeonato_id)
        estadisticas = EstadisticaJugadorVideojuegos.objects.filter(campeonato=campeonato).order_by('-partidas_ganadas')
    else:
        estadisticas = EstadisticaJugadorVideojuegos.objects.all().order_by('-partidas_ganadas')

    campeonatos = Campeonato.objects.all()
    context = {
        'estadisticas': estadisticas,
        'campeonatos': campeonatos,
        'selected_campeonato_id': int(campeonato_id) if campeonato_id else None
    }
    return render(request, 'estadisticas/estadisticas_videojuegos.html', context)

@login_required
def mis_estadisticas(request):
    jugador = get_object_or_404(Jugador, usuario=request.user)
    
    estadisticas_futbol = EstadisticaJugadorFutbol.objects.filter(jugador=jugador)
    estadisticas_basquet = EstadisticaJugadorBasquet.objects.filter(jugador=jugador)
    estadisticas_ajedrez = EstadisticaJugadorAjedrez.objects.filter(jugador=jugador)
    estadisticas_ecuaboly = EstadisticaJugadorEcuaboly.objects.filter(jugador=jugador)
    estadisticas_pingpong = EstadisticaJugadorPingPong.objects.filter(jugador=jugador)
    estadisticas_tenis = EstadisticaJugadorTenis.objects.filter(jugador=jugador)
    estadisticas_futbolin = EstadisticaJugadorFutbolin.objects.filter(jugador=jugador)
    estadisticas_videojuegos = EstadisticaJugadorVideojuegos.objects.filter(jugador=jugador)

    context = {
        'jugador': jugador,
        'estadisticas_futbol': estadisticas_futbol,
        'estadisticas_basquet': estadisticas_basquet,
        'estadisticas_ajedrez': estadisticas_ajedrez,
        'estadisticas_ecuaboly': estadisticas_ecuaboly,
        'estadisticas_pingpong': estadisticas_pingpong,
        'estadisticas_tenis': estadisticas_tenis,
        'estadisticas_futbolin': estadisticas_futbolin,
        'estadisticas_videojuegos': estadisticas_videojuegos,
    }
    return render(request, 'estadisticas/mis_estadisticas.html', context)


@login_required
@user_passes_test(es_admin_o_delegado)
def export_estadisticas_futbol_pdf(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorFutbol.objects.filter(campeonato_id=campeonato_id).order_by('-goles')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorFutbol.objects.all().order_by('-goles')
        campeonato_nombre = "Todos los Campeonatos"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom style for title
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['h2'],
        alignment=1, # CENTER
        spaceAfter=14
    )

    # Custom style for headers
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=1, # CENTER
        spaceAfter=6
    )

    # Custom style for content
    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        alignment=1, # CENTER
        spaceAfter=2
    )

    elements = []
    elements.append(Paragraph(f"Estadísticas de Fútbol - {campeonato_nombre}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    data = [
        [
            Paragraph("Jugador", header_style),
            Paragraph("Equipo", header_style),
            Paragraph("Campeonato", header_style),
            Paragraph("PJ", header_style),
            Paragraph("Goles", header_style),
            Paragraph("TA", header_style),
            Paragraph("TR", header_style)
        ]
    ]
    for stat in estadisticas:
        data.append([
            Paragraph(stat.jugador.usuario.username, content_style),
            Paragraph(stat.jugador.equipo.nombre, content_style),
            Paragraph(stat.campeonato.nombre, content_style),
            Paragraph(str(stat.partidos_jugados), content_style),
            Paragraph(str(stat.goles), content_style),
            Paragraph(str(stat.tarjetas_amarillas), content_style),
            Paragraph(str(stat.tarjetas_rojas), content_style)
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')), # Dark header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # White header text
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')), # Light row background
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')), # Light grid lines
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')), # Border around table
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

@login_required
def export_estadisticas_futbol_excel(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorFutbol.objects.filter(campeonato_id=campeonato_id).order_by('-goles')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorFutbol.objects.all().order_by('-goles')
        campeonato_nombre = "Todos los Campeonatos"

    data = []
    for stat in estadisticas:
        data.append({
            'Jugador': stat.jugador.usuario.username,
            'Equipo': stat.jugador.equipo.nombre,
            'Campeonato': stat.campeonato.nombre,
            'Partidos Jugados': stat.partidos_jugados,
            'Goles': stat.goles,
            'Tarjetas Amarillas': stat.tarjetas_amarillas,
            'Tarjetas Rojas': stat.tarjetas_rojas,
        })

    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Estadisticas Futbol')
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=estadisticas_futbol_{campeonato_nombre.replace(" ", "_")}.xlsx'
    return response

@login_required
def export_estadisticas_basquet_pdf(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorBasquet.objects.filter(campeonato_id=campeonato_id).order_by('-canastas')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorBasquet.objects.all().order_by('-canastas')
        campeonato_nombre = "Todos los Campeonatos"

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
    elements.append(Paragraph(f"Estadísticas de Baloncesto - {campeonato_nombre}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    data = [
        [
            Paragraph("Jugador", header_style),
            Paragraph("Equipo", header_style),
            Paragraph("Campeonato", header_style),
            Paragraph("PJ", header_style),
            Paragraph("Canastas", header_style),
            Paragraph("Rebotes", header_style),
            Paragraph("Asistencias", header_style)
        ]
    ]
    for stat in estadisticas:
        data.append([
            Paragraph(stat.jugador.usuario.username, content_style),
            Paragraph(stat.jugador.equipo.nombre, content_style),
            Paragraph(stat.campeonato.nombre, content_style),
            Paragraph(str(stat.partidos_jugados), content_style),
            Paragraph(str(stat.canastas), content_style),
            Paragraph(str(stat.rebotes), content_style),
            Paragraph(str(stat.asistencias), content_style)
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
def export_estadisticas_basquet_excel(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorBasquet.objects.filter(campeonato_id=campeonato_id).order_by('-canastas')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorBasquet.objects.all().order_by('-canastas')
        campeonato_nombre = "Todos los Campeonatos"

    data = []
    for stat in estadisticas:
        data.append({
            'Jugador': stat.jugador.usuario.username,
            'Equipo': stat.jugador.equipo.nombre,
            'Campeonato': stat.campeonato.nombre,
            'Partidos Jugados': stat.partidos_jugados,
            'Canastas': stat.canastas,
            'Rebotes': stat.rebotes,
            'Asistencias': stat.asistencias,
        })

    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Estadisticas Basquet')
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=estadisticas_basquet_{campeonato_nombre.replace(" ", "_")}.xlsx'
    return response

@login_required
def export_estadisticas_ajedrez_pdf(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorAjedrez.objects.filter(campeonato_id=campeonato_id).order_by('-partidas_ganadas')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorAjedrez.objects.all().order_by('-partidas_ganadas')
        campeonato_nombre = "Todos los Campeonatos"

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
    elements.append(Paragraph(f"Estadísticas de Ajedrez - {campeonato_nombre}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    data = [
        [
            Paragraph("Jugador", header_style),
            Paragraph("Equipo", header_style),
            Paragraph("Campeonato", header_style),
            Paragraph("PJ", header_style),
            Paragraph("PG", header_style),
            Paragraph("PE", header_style),
            Paragraph("PP", header_style)
        ]
    ]
    for stat in estadisticas:
        data.append([
            Paragraph(stat.jugador.usuario.username, content_style),
            Paragraph(stat.jugador.equipo.nombre, content_style),
            Paragraph(stat.campeonato.nombre, content_style),
            Paragraph(str(stat.partidas_jugadas), content_style),
            Paragraph(str(stat.partidas_ganadas), content_style),
            Paragraph(str(stat.partidas_empatadas), content_style),
            Paragraph(str(stat.partidas_perdidas), content_style)
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
def export_estadisticas_ajedrez_excel(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorAjedrez.objects.filter(campeonato_id=campeonato_id).order_by('-partidas_ganadas')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorAjedrez.objects.all().order_by('-partidas_ganadas')
        campeonato_nombre = "Todos los Campeonatos"

    data = []
    for stat in estadisticas:
        data.append({
            'Jugador': stat.jugador.usuario.username,
            'Equipo': stat.jugador.equipo.nombre,
            'Campeonato': stat.campeonato.nombre,
            'Partidas Jugadas': stat.partidas_jugadas,
            'Partidas Ganadas': stat.partidas_ganadas,
            'Partidas Empatadas': stat.partidas_empatadas,
            'Partidas Perdidas': stat.partidas_perdidas,
        })

    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Estadisticas Ajedrez')
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=estadisticas_ajedrez_{campeonato_nombre.replace(" ", "_")}.xlsx'
    return response

@login_required
def export_estadisticas_ecuaboly_pdf(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorEcuaboly.objects.filter(campeonato_id=campeonato_id).order_by('-sets_ganados')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorEcuaboly.objects.all().order_by('-sets_ganados')
        campeonato_nombre = "Todos los Campeonatos"

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
    elements.append(Paragraph(f"Estadísticas de Ecuaboly - {campeonato_nombre}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    data = [
        [
            Paragraph("Jugador", header_style),
            Paragraph("Equipo", header_style),
            Paragraph("Campeonato", header_style),
            Paragraph("PJ", header_style),
            Paragraph("Sets Ganados", header_style),
            Paragraph("Sets Perdidos", header_style)
        ]
    ]
    for stat in estadisticas:
        data.append([
            Paragraph(stat.jugador.usuario.username, content_style),
            Paragraph(stat.jugador.equipo.nombre, content_style),
            Paragraph(stat.campeonato.nombre, content_style),
            Paragraph(str(stat.partidos_jugados), content_style),
            Paragraph(str(stat.sets_ganados), content_style),
            Paragraph(str(stat.sets_perdidos), content_style)
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
def export_estadisticas_ecuaboly_excel(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorEcuaboly.objects.filter(campeonato_id=campeonato_id).order_by('-sets_ganados')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorEcuaboly.objects.all().order_by('-sets_ganados')
        campeonato_nombre = "Todos los Campeonatos"

    data = []
    for stat in estadisticas:
        data.append({
            'Jugador': stat.jugador.usuario.username,
            'Equipo': stat.jugador.equipo.nombre,
            'Campeonato': stat.campeonato.nombre,
            'Partidos Jugados': stat.partidos_jugados,
            'Sets Ganados': stat.sets_ganados,
            'Sets Perdidos': stat.sets_perdidos,
        })

    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Estadisticas Ecuaboly')
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=estadisticas_ecuaboly_{campeonato_nombre.replace(" ", "_")}.xlsx'
    return response

@login_required
def export_estadisticas_futbolin_pdf(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorFutbolin.objects.filter(campeonato_id=campeonato_id).order_by('-goles')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorFutbolin.objects.all().order_by('-goles')
        campeonato_nombre = "Todos los Campeonatos"

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
    elements.append(Paragraph(f"Estadísticas de Futbolín - {campeonato_nombre}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    data = [
        [
            Paragraph("Jugador", header_style),
            Paragraph("Equipo", header_style),
            Paragraph("Campeonato", header_style),
            Paragraph("PJ", header_style),
            Paragraph("PG", header_style),
            Paragraph("PP", header_style),
            Paragraph("Goles", header_style)
        ]
    ]
    for stat in estadisticas:
        data.append([
            Paragraph(stat.jugador.usuario.username, content_style),
            Paragraph(stat.jugador.equipo.nombre, content_style),
            Paragraph(stat.campeonato.nombre, content_style),
            Paragraph(str(stat.partidos_jugados), content_style),
            Paragraph(str(stat.partidos_ganados), content_style),
            Paragraph(str(stat.partidos_perdidos), content_style),
            Paragraph(str(stat.goles), content_style)
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
def export_estadisticas_futbolin_excel(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorFutbolin.objects.filter(campeonato_id=campeonato_id).order_by('-goles')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorFutbolin.objects.all().order_by('-goles')
        campeonato_nombre = "Todos los Campeonatos"

    data = []
    for stat in estadisticas:
        data.append({
            'Jugador': stat.jugador.usuario.username,
            'Equipo': stat.jugador.equipo.nombre,
            'Campeonato': stat.campeonato.nombre,
            'Partidos Jugados': stat.partidos_jugados,
            'Partidos Ganados': stat.partidos_ganados,
            'Partidos Perdidos': stat.partidos_perdidos,
            'Goles': stat.goles,
        })

    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Estadisticas Futbolin')
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=estadisticas_futbolin_{campeonato_nombre.replace(" ", "_")}.xlsx'
    return response

@login_required
def export_estadisticas_pingpong_pdf(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorPingPong.objects.filter(campeonato_id=campeonato_id).order_by('-partidos_ganados')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorPingPong.objects.all().order_by('-partidos_ganados')
        campeonato_nombre = "Todos los Campeonatos"

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
    elements.append(Paragraph(f"Estadísticas de Ping Pong - {campeonato_nombre}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    data = [
        [
            Paragraph("Jugador", header_style),
            Paragraph("Equipo", header_style),
            Paragraph("Campeonato", header_style),
            Paragraph("PJ", header_style),
            Paragraph("PG", header_style),
            Paragraph("PP", header_style)
        ]
    ]
    for stat in estadisticas:
        data.append([
            Paragraph(stat.jugador.usuario.username, content_style),
            Paragraph(stat.jugador.equipo.nombre, content_style),
            Paragraph(stat.campeonato.nombre, content_style),
            Paragraph(str(stat.partidos_jugados), content_style),
            Paragraph(str(stat.partidos_ganados), content_style),
            Paragraph(str(stat.partidos_perdidos), content_style)
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
def export_estadisticas_pingpong_excel(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorPingPong.objects.filter(campeonato_id=campeonato_id).order_by('-partidos_ganados')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorPingPong.objects.all().order_by('-partidos_ganados')
        campeonato_nombre = "Todos los Campeonatos"

    data = []
    for stat in estadisticas:
        data.append({
            'Jugador': stat.jugador.usuario.username,
            'Equipo': stat.jugador.equipo.nombre,
            'Campeonato': stat.campeonato.nombre,
            'Partidos Jugados': stat.partidos_jugados,
            'Partidos Ganados': stat.partidos_ganados,
            'Partidos Perdidos': stat.partidos_perdidos,
        })

    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Estadisticas Ping Pong')
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=estadisticas_pingpong_{campeonato_nombre.replace(" ", "_")}.xlsx'
    return response

@login_required
@user_passes_test(es_admin_o_delegado)
def export_estadisticas_tenis_pdf(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorTenis.objects.filter(campeonato_id=campeonato_id).order_by('-sets_ganados')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorTenis.objects.all().order_by('-sets_ganados')
        campeonato_nombre = "Todos los Campeonatos"

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
    elements.append(Paragraph(f"Estadísticas de Tenis - {campeonato_nombre}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    data = [
        [
            Paragraph("Jugador", header_style),
            Paragraph("Equipo", header_style),
            Paragraph("Campeonato", header_style),
            Paragraph("PJ", header_style),
            Paragraph("Sets Ganados", header_style),
            Paragraph("Sets Perdidos", header_style)
        ]
    ]
    for stat in estadisticas:
        data.append([
            Paragraph(stat.jugador.usuario.username, content_style),
            Paragraph(stat.jugador.equipo.nombre, content_style),
            Paragraph(stat.campeonato.nombre, content_style),
            Paragraph(str(stat.partidos_jugados), content_style),
            Paragraph(str(stat.sets_ganados), content_style),
            Paragraph(str(stat.sets_perdidos), content_style)
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
def export_estadisticas_tenis_excel(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorTenis.objects.filter(campeonato_id=campeonato_id).order_by('-sets_ganados')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorTenis.objects.all().order_by('-sets_ganados')
        campeonato_nombre = "Todos los Campeonatos"

    data = []
    for stat in estadisticas:
        data.append({
            'Jugador': stat.jugador.usuario.username,
            'Equipo': stat.jugador.equipo.nombre,
            'Campeonato': stat.campeonato.nombre,
            'Partidos Jugados': stat.partidos_jugados,
            'Sets Ganados': stat.sets_ganados,
            'Sets Perdidos': stat.sets_perdidos,
        })

    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Estadisticas Tenis')
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=estadisticas_tenis_{campeonato_nombre.replace(" ", "_")}.xlsx'
    return response

@login_required
@user_passes_test(es_admin_o_delegado)
def export_estadisticas_videojuegos_pdf(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorVideojuegos.objects.filter(campeonato_id=campeonato_id).order_by('-partidas_ganadas')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorVideojuegos.objects.all().order_by('-partidas_ganadas')
        campeonato_nombre = "Todos los Campeonatos"

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
    elements.append(Paragraph(f"Estadísticas de Videojuegos - {campeonato_nombre}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    data = [
        [
            Paragraph("Jugador", header_style),
            Paragraph("Equipo", header_style),
            Paragraph("Campeonato", header_style),
            Paragraph("PJ", header_style),
            Paragraph("PG", header_style),
            Paragraph("PP", header_style)
        ]
    ]
    for stat in estadisticas:
        data.append([
            Paragraph(stat.jugador.usuario.username, content_style),
            Paragraph(stat.jugador.equipo.nombre, content_style),
            Paragraph(stat.campeonato.nombre, content_style),
            Paragraph(str(stat.partidas_jugadas), content_style),
            Paragraph(str(stat.partidas_ganadas), content_style),
            Paragraph(str(stat.partidas_perdidas), content_style)
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
def export_estadisticas_videojuegos_excel(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorVideojuegos.objects.filter(campeonato_id=campeonato_id).order_by('-partidas_ganadas')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorVideojuegos.objects.all().order_by('-partidas_ganadas')
        campeonato_nombre = "Todos los Campeonatos"

    data = []
    for stat in estadisticas:
        data.append({
            'Jugador': stat.jugador.usuario.username,
            'Equipo': stat.jugador.equipo.nombre,
            'Campeonato': stat.campeonato.nombre,
            'Partidas Jugadas': stat.partidas_jugadas,
            'Partidas Ganadas': stat.partidas_ganadas,
            'Partidas Perdidas': stat.partidas_perdidas,
        })

    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Estadisticas Videojuegos')
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=estadisticas_videojuegos_{campeonato_nombre.replace(" ", "_")}.xlsx'
    return response


@login_required
@user_passes_test(es_admin_o_delegado)
def export_estadisticas_futbol_pdf(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorFutbol.objects.filter(campeonato_id=campeonato_id).order_by('-goles')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorFutbol.objects.all().order_by('-goles')
        campeonato_nombre = "Todos los Campeonatos"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom style for title
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['h2'],
        alignment=1, # CENTER
        spaceAfter=14
    )

    # Custom style for headers
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=1, # CENTER
        spaceAfter=6
    )

    # Custom style for content
    content_style = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        alignment=1, # CENTER
        spaceAfter=2
    )

    elements = []
    elements.append(Paragraph(f"Estadísticas de Fútbol - {campeonato_nombre}", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    data = [
        [
            Paragraph("Jugador", header_style),
            Paragraph("Equipo", header_style),
            Paragraph("Campeonato", header_style),
            Paragraph("PJ", header_style),
            Paragraph("Goles", header_style),
            Paragraph("TA", header_style),
            Paragraph("TR", header_style)
        ]
    ]
    for stat in estadisticas:
        data.append([
            Paragraph(stat.jugador.usuario.username, content_style),
            Paragraph(stat.jugador.equipo.nombre, content_style),
            Paragraph(stat.campeonato.nombre, content_style),
            Paragraph(str(stat.partidos_jugados), content_style),
            Paragraph(str(stat.goles), content_style),
            Paragraph(str(stat.tarjetas_amarillas), content_style),
            Paragraph(str(stat.tarjetas_rojas), content_style)
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')), # Dark header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), # White header text
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')), # Light row background
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')), # Light grid lines
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')), # Border around table
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

@login_required
def export_estadisticas_futbol_excel(request):
    campeonato_id = request.GET.get('campeonato_id')
    if campeonato_id:
        estadisticas = EstadisticaJugadorFutbol.objects.filter(campeonato_id=campeonato_id).order_by('-goles')
        campeonato_nombre = Campeonato.objects.get(id=campeonato_id).nombre
    else:
        estadisticas = EstadisticaJugadorFutbol.objects.all().order_by('-goles')
        campeonato_nombre = "Todos los Campeonatos"

    data = []
    for stat in estadisticas:
        data.append({
            'Jugador': stat.jugador.usuario.username,
            'Equipo': stat.jugador.equipo.nombre,
            'Campeonato': stat.campeonato.nombre,
            'Partidos Jugados': stat.partidos_jugados,
            'Goles': stat.goles,
            'Tarjetas Amarillas': stat.tarjetas_amarillas,
            'Tarjetas Rojas': stat.tarjetas_rojas,
        })

    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Estadisticas Futbol')
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=estadisticas_futbol_{campeonato_nombre.replace(" ", "_")}.xlsx'
    return response