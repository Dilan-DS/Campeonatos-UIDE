from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import Partido, Usuario, Arbitro, Campeonato, Equipo, EstadisticaJugadorFutbol, Suspension, Jugador
from django.db.models import Q
from django.contrib import messages
import json
from django.db import transaction
from django.utils import timezone
from core.forms import ArbitroActaForm
import datetime # Added datetime
from django.core.exceptions import ValidationError # Added ValidationError

# --- ACTA ÁRBITRO HELPERS ---
def _leer_snapshot(partido):
    try:
        return json.loads(partido.suspensiones_json or "{}")
    except Exception:
        return {}

def _guardar_snapshot(partido, snap: dict):
    partido.suspensiones_json = json.dumps(snap, default=str)
    partido.save(update_fields=["suspensiones_json"])

def _aplicar_delta_estadisticas(campeonato, jugador, goles, ama, roja, pj):
    est, _ = EstadisticaJugadorFutbol.objects.get_or_create(campeonato=campeonato, jugador=jugador)
    est.partidos_jugados += pj
    est.goles += goles
    est.tarjetas_amarillas += ama
    est.tarjetas_rojas += roja
    est.save()

def _revertir_snapshot(partido):
    snap = _leer_snapshot(partido)
    # revertir estadísticas
    for it in snap.get("jugadores", []):
        j_id = it.get("jugador_id")
        if not j_id:
            continue
        try:
            j = Jugador.objects.get(id=j_id)
            est = EstadisticaJugadorFutbol.objects.get(campeonato=partido.campeonato, jugador=j)
            est.goles = max(0, est.goles - int(it.get("goles", 0)))
            est.tarjetas_amarillas = max(0, est.tarjetas_amarillas - int(it.get("amarillas", 0)))
            est.tarjetas_rojas = max(0, est.tarjetas_rojas - int(it.get("rojas", 0)))
            est.partidos_jugados = max(0, est.partidos_jugados - int(it.get("pj", 0)))
            est.save()
        except (Jugador.DoesNotExist, EstadisticaJugadorFutbol.DoesNotExist):
            pass
    # borrar suspensiones creadas por la edición anterior del acta
    for sid in snap.get("suspensiones_ids", []):
        Suspension.objects.filter(id=sid).delete()
    _guardar_snapshot(partido, {})

@login_required
@transaction.atomic
def acta_partido_arbitro(request, pk):
    partido = get_object_or_404(Partido, pk=pk)
    # Permisos: sólo árbitro asignado
    if not request.user.is_authenticated or not hasattr(partido, "arbitro") or partido.arbitro is None or partido.arbitro.usuario_id != request.user.id:
        messages.error(request, "No tienes permiso para cargar el acta de este partido.")
        return redirect("detalle_partido", partido_id=partido.id)

    jugadores_local = Jugador.objects.filter(equipo=partido.equipo_local).select_related("usuario")
    jugadores_vis   = Jugador.objects.filter(equipo=partido.equipo_visitante).select_related("usuario")

    if request.method == "POST":
        form = ArbitroActaForm(request.POST, jugadores_local=jugadores_local, jugadores_visitante=jugadores_vis)
        if form.is_valid():
            # Validar sumas
            sum_loc = form.total_goles_por_equipo(jugadores_local)
            sum_vis = form.total_goles_por_equipo(jugadores_vis)
            if sum_loc != form.cleaned_data["resultado_local"] or sum_vis != form.cleaned_data["resultado_visitante"]:
                messages.error(request, "La suma de goles por jugador no coincide con el resultado ingresado.")
                # Prepare context for re-rendering with errors
                filas_local = [(j, form[f"goles_{j.id}"], form[f"amarillas_{j.id}"], form[f"roja_{j.id}"], form[f"susp_{j.id}"], form[f"susp_ini_{j.id}"], form[f"susp_fin_{j.id}"], form[f"susp_mot_{j.id}"]) for j in jugadores_local]
                filas_vis = [(j, form[f"goles_{j.id}"], form[f"amarillas_{j.id}"], form[f"roja_{j.id}"], form[f"susp_{j.id}"], form[f"susp_ini_{j.id}"], form[f"susp_fin_{j.id}"], form[f"susp_mot_{j.id}"]) for j in jugadores_vis]
                return render(request, "arbitro/acta_partido.html", {
                    "partido": partido,
                    "form": form,
                    "filas_local": filas_local,
                    "filas_vis": filas_vis
                })

            # 1) Revertir snapshot previo si lo hay
            _revertir_snapshot(partido)

            # 2) Aplicar nuevo snapshot
            snap = {"jugadores": [], "suspensiones_ids": []}
            # por equipo
            for j in list(jugadores_local) + list(jugadores_vis):
                goles = int(form.cleaned_data.get(f"goles_{j.id}", 0) or 0)
                ama   = int(form.cleaned_data.get(f"amarillas_{j.id}", 0) or 0)
                roja  = int(form.cleaned_data.get(f"roja_{j.id}", 0) or 0)
                pj    = 1 if (goles or ama or roja) else 0
                if any([goles, ama, roja, pj]):
                    _aplicar_delta_estadisticas(partido.campeonato, j, goles, ama, roja, pj)
                snap["jugadores"].append({
                    "jugador_id": j.id,
                    "goles": goles,
                    "amarillas": ama,
                    "rojas": roja,
                    "pj": pj
                })

                # Crear Suspensiones
                if form.cleaned_data.get(f"susp_{j.id}"):
                    hoy = datetime.date.today()
                    ini_default = max(hoy, partido.fecha)
                    ini = form.cleaned_data.get(f"susp_ini_{j.id}") or ini_default
                    fin = form.cleaned_data.get(f"susp_fin_{j.id}") or ini
                    mot = form.cleaned_data.get(f"susp_mot_{j.id}") or f"Expulsión en partido #{partido.id}"

                    if fin < ini:
                        messages.error(request, f"La suspensión de {j.usuario.username} tiene fecha fin anterior al inicio.")
                        # Prepare context for re-rendering with errors
                        filas_local = [(j, form[f"goles_{j.id}"], form[f"amarillas_{j.id}"], form[f"roja_{j.id}"], form[f"susp_{j.id}"], form[f"susp_ini_{j.id}"], form[f"susp_fin_{j.id}"], form[f"susp_mot_{j.id}"]) for j in jugadores_local]
                        filas_vis = [(j, form[f"goles_{j.id}"], form[f"amarillas_{j.id}"], form[f"roja_{j.id}"], form[f"susp_{j.id}"], form[f"susp_ini_{j.id}"], form[f"susp_fin_{j.id}"], form[f"susp_mot_{j.id}"]) for j in jugadores_vis]
                        return render(request, "arbitro/acta_partido.html", {
                            "partido": partido,
                            "form": form,
                            "filas_local": filas_local,
                            "filas_vis": filas_vis
                        })

                    s = Suspension.objects.create(jugador=j, fecha_inicio=ini, fecha_fin=fin, motivo=mot)
                    snap["suspensiones_ids"].append(s.id)

            # 3) Actualizar partido
            partido.resultado_local = form.cleaned_data["resultado_local"]
            partido.resultado_visitante = form.cleaned_data["resultado_visitante"]
            partido.tarjetas_amarillas_local = int(form.cleaned_data.get("tarjetas_amarillas_local") or 0)
            partido.tarjetas_amarillas_visitante = int(form.cleaned_data.get("tarjetas_amarillas_visitante") or 0)
            partido.tarjetas_rojas_local = int(form.cleaned_data.get("tarjetas_rojas_local") or 0)
            partido.tarjetas_rojas_visitante = int(form.cleaned_data.get("tarjetas_rojas_visitante") or 0)
            obs = form.cleaned_data.get("observaciones") or ""
            partido.observaciones_arbitro = obs
            partido.estado = "FINALIZADO"
            partido.save()
            _guardar_snapshot(partido, snap)

            messages.success(request, "Acta guardada correctamente.")
            return redirect("detalle_partido", partido_id=partido.id)
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
            filas_local = [(j, form[f"goles_{j.id}"], form[f"amarillas_{j.id}"], form[f"roja_{j.id}"], form[f"susp_{j.id}"], form[f"susp_ini_{j.id}"], form[f"susp_fin_{j.id}"], form[f"susp_mot_{j.id}"]) for j in jugadores_local]
            filas_vis = [(j, form[f"goles_{j.id}"], form[f"amarillas_{j.id}"], form[f"roja_{j.id}"], form[f"susp_{j.id}"], form[f"susp_ini_{j.id}"], form[f"susp_fin_{j.id}"], form[f"susp_mot_{j.id}"]) for j in jugadores_vis]
            return render(request, "arbitro/acta_partido.html", {
                "partido": partido,
                "form": form,
                "filas_local": filas_local,
                "filas_vis": filas_vis,
            })
    
    # Prepare context for initial GET
    form = ArbitroActaForm(jugadores_local=jugadores_local, jugadores_visitante=jugadores_vis)
    filas_local = [(j, form[f"goles_{j.id}"], form[f"amarillas_{j.id}"], form[f"roja_{j.id}"], form[f"susp_{j.id}"], form[f"susp_ini_{j.id}"], form[f"susp_fin_{j.id}"], form[f"susp_mot_{j.id}"]) for j in jugadores_local]
    filas_vis = [(j, form[f"goles_{j.id}"], form[f"amarillas_{j.id}"], form[f"roja_{j.id}"], form[f"susp_{j.id}"], form[f"susp_ini_{j.id}"], form[f"susp_fin_{j.id}"], form[f"susp_mot_{j.id}"]) for j in jugadores_vis]

    return render(request, "arbitro/acta_partido.html", {
        "partido": partido,
        "form": form,
        "filas_local": filas_local,
        "filas_vis": filas_vis
    })

# Permisos helpers
def es_admin(user):
    return user.is_authenticated and getattr(user, "rol", "") == "ADMIN"

def es_arbitro(user):
    return user.is_authenticated and getattr(user, "rol", "") == "ARBITRO"

# FBV listar_arbitros (ADMIN)
@login_required
@user_passes_test(es_admin, login_url='/login/')
def listar_arbitros(request):
    arbitros = Arbitro.objects.all().select_related('usuario')
    return render(request, 'arbitro/listar.html', {'arbitros': arbitros})

# FBV mis_partidos_arbitro (ÁRBITRO)
@login_required
@user_passes_test(es_arbitro, login_url='/login/')
def mis_partidos_arbitro(request):
    try:
        # Asegurarse de que request.user.arbitro exista y sea el objeto Arbitro
        # Si el campo arbitro en Partido es FK a Usuario, usar request.user directamente
        # Si es FK a Arbitro, usar request.user.arbitro
        # Asumiendo que Partido.arbitro es FK a Arbitro, y Arbitro tiene OneToOne a Usuario
        arbitro_obj = request.user.arbitro
        partidos = (
            Partido.objects
            .filter(arbitro=arbitro_obj)
            .select_related('equipo_local','equipo_visitante','campeonato')
            .order_by('fecha','hora','id')
        )
        return render(request, 'arbitro/mis_partidos.html', {'partidos': partidos})
    except Arbitro.DoesNotExist:
        messages.error(request, "No estás registrado como árbitro o tu perfil de árbitro no está completo.")
        return redirect('vista_inicio') # Redirigir a una página segura

# FBV registrar_resultado_partido (ÁRBITRO)
@login_required
@user_passes_test(es_arbitro, login_url='/login/')
def registrar_resultado_partido(request, partido_id):
    try:
        arbitro_obj = request.user.arbitro
        partido = get_object_or_404(Partido, pk=partido_id, arbitro=arbitro_obj) # Ensure arbitro matches
    except Arbitro.DoesNotExist:
        messages.error(request, "No estás registrado como árbitro o tu perfil de árbitro no está completo.")
        return redirect('vista_inicio')

    if request.method == 'POST':
        partido.resultado_local = int(request.POST.get('resultado_local', 0))
        partido.resultado_visitante = int(request.POST.get('resultado_visitante', 0))
        partido.estado = 'FINALIZADO'
        partido.save()
        messages.success(request, "Resultado registrado correctamente y partido finalizado.")
        return redirect('mis_partidos_arbitro')
    
    return render(request, 'arbitro/registrar_resultado.html', {'partido': partido})

# FBV disciplinario_partido (ÁRBITRO)
@login_required
@user_passes_test(es_arbitro, login_url='/login/')
def disciplinario_partido(request, partido_id):
    try:
        arbitro_obj = request.user.arbitro
        partido = get_object_or_404(Partido, pk=partido_id, arbitro=arbitro_obj) # Ensure arbitro matches
    except Arbitro.DoesNotExist:
        messages.error(request, "No estás registrado como árbitro o tu perfil de árbitro no está completo.")
        return redirect('vista_inicio')

    if request.method == 'POST':
        # Asumiendo campos en el modelo Partido o un modelo relacionado
        partido.tarjetas_amarillas_local = int(request.POST.get('tarjetas_amarillas_local', 0))
        partido.tarjetas_amarillas_visitante = int(request.POST.get('tarjetas_amarillas_visitante', 0))
        partido.tarjetas_rojas_local = int(request.POST.get('tarjetas_rojas_local', 0))
        partido.tarjetas_rojas_visitante = int(request.POST.get('tarjetas_rojas_visitante', 0))
        partido.observaciones_arbitro = request.POST.get('observaciones_arbitro', '')
        # suspensiones_json: Esto requeriría más lógica para parsear JSON o un formato específico
        # Por ahora, solo guardamos las observaciones.
        partido.save()
        messages.success(request, "Datos disciplinarios registrados correctamente.")
        return redirect('mis_partidos_arbitro')
    
    return render(request, 'arbitro/disciplinario.html', {'partido': partido})

@login_required
@user_passes_test(es_arbitro, login_url='/login/')
def ver_tabla_posiciones_arbitro(request, campeonato_id):
    campeonato = get_object_or_404(Campeonato, pk=campeonato_id)
    equipos = Equipo.objects.filter(campeonato=campeonato)
    
    tabla = []
    for equipo in equipos:
        partidos_local = Partido.objects.filter(equipo_local=equipo, estado='FINALIZADO')
        partidos_visitante = Partido.objects.filter(equipo_visitante=equipo, estado='FINALIZADO')

        pj = partidos_local.count() + partidos_visitante.count()
        pg = 0
        pe = 0
        pp = 0
        gf = 0
        gc = 0

        for partido in partidos_local:
            if partido.resultado_local > partido.resultado_visitante:
                pg += 1
            elif partido.resultado_local == partido.resultado_visitante:
                pe += 1
            else:
                pp += 1
            gf += partido.resultado_local or 0
            gc += partido.resultado_visitante or 0

        for partido in partidos_visitante:
            if partido.resultado_visitante > partido.resultado_local:
                pg += 1
            elif partido.resultado_visitante == partido.resultado_local:
                pe += 1
            else:
                pp += 1
            gf += partido.resultado_visitante or 0
            gc += partido.resultado_local or 0
            
        puntos = (pg * 3) + (pe * 1)
        gd = gf - gc

        tabla.append({
            'equipo': equipo,
            'pj': pj,
            'pg': pg,
            'pe': pe,
            'pp': pp,
            'gf': gf,
            'gc': gc,
            'gd': gd,
            'puntos': puntos,
        })

    tabla.sort(key=lambda x: (x['puntos'], x['gd']), reverse=True)

    return render(request, 'campeonato/tabla_posiciones.html', {
        'campeonato': campeonato,
        'tabla': tabla
    })

@login_required
@user_passes_test(es_arbitro, login_url='/login/')
def historial_arbitros(request):
    try:
        arbitro_obj = request.user.arbitro
        partidos_finalizados = (
            Partido.objects
            .filter(arbitro=arbitro_obj, estado='FINALIZADO')
            .select_related('equipo_local','equipo_visitante','campeonato')
            .order_by('-fecha','-hora','-id')
        )
        return render(request, 'arbitro/historial.html', {'partidos': partidos_finalizados})
    except Arbitro.DoesNotExist:
        messages.error(request, "No estás registrado como árbitro o tu perfil de árbitro no está completo.")
        return redirect('vista_inicio')