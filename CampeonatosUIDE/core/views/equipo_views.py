# core/views/equipo_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.http import HttpResponseForbidden

from core.models import (
    Equipo, Campeonato, Jugador,
    EstadisticaJugadorFutbol, EstadisticaJugadorBasquet, EstadisticaJugadorAjedrez,
    EstadisticaJugadorEcuaboly, EstadisticaJugadorPingPong, EstadisticaJugadorTenis,
    EstadisticaJugadorVideojuegos, EstadisticaJugadorFutbolin,
)
from core.forms import EquipoForm, PagoForm  # PagoForm se conserva por compatibilidad

# ---------------------------
# Helpers
# ---------------------------
def es_admin_o_delegado(user):
    return getattr(user, "rol", None) in ["ADMIN", "DELEGADO"]


def _get_campeonato_id(request, kwargs=None):
    """
    Resuelve campeonato_id desde kwargs, GET, POST o session.
    Si no hay, toma el activo más reciente.
    """
    kwargs = kwargs or {}
    cid = (
        kwargs.get("campeonato_id")
        or request.GET.get("campeonato_id")
        or request.POST.get("campeonato_id")
        or request.session.get("campeonato_id")
    )
    if not cid:
        camp = Campeonato.objects.filter(activo="SI").order_by("-fecha_inicio").first()
        cid = camp.id if camp else None
    if cid:
        request.session["campeonato_id"] = int(cid)
    return cid

# ---------------------------
# Vistas de jugadores/equipo (públicas por rol)
# ---------------------------
@login_required
def ver_equipo_jugador(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)

    # Si es jugador, forzar su propio equipo
    if getattr(request.user, "rol", "").upper() == "JUGADOR":
        try:
            jugador = Jugador.objects.get(usuario=request.user)
            equipo = jugador.equipo
        except Jugador.DoesNotExist:
            messages.error(request, "No estás registrado en ningún equipo.")
            return redirect("jugador_dashboard")

    jugadores_data = []
    campeonato = equipo.campeonato
    deporte_nombre = campeonato.deporte.nombre.upper()

    for jugador_item in equipo.jugadores.all():
        player_stats = None
        if deporte_nombre == "FUTBOL":
            player_stats = EstadisticaJugadorFutbol.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == "BASQUET":
            player_stats = EstadisticaJugadorBasquet.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == "AJEDREZ":
            player_stats = EstadisticaJugadorAjedrez.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == "ECUABOLY":
            player_stats = EstadisticaJugadorEcuaboly.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == "PING PONG":
            player_stats = EstadisticaJugadorPingPong.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == "TENIS":
            player_stats = EstadisticaJugadorTenis.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == "VIDEOJUEGOS":
            player_stats = EstadisticaJugadorVideojuegos.objects.filter(jugador=jugador_item, campeonato=campeonato).first()
        elif deporte_nombre == "FUTBOLIN":
            player_stats = EstadisticaJugadorFutbolin.objects.filter(jugador=jugador_item, campeonato=campeonato).first()

        jugadores_data.append({
            "jugador": jugador_item,
            "stats": player_stats,
            "deporte_nombre": deporte_nombre,
            "posicion": jugador_item.posicion,
        })

    return render(
        request,
        "equipo/jugadores_equipo.html",
        {"equipo": equipo, "jugadores_data": jugadores_data, "is_jugador_view": True},
    )

# ---------------------------
# CRUD de equipos (ADMIN/DELEGADO)
# ---------------------------
@login_required
@user_passes_test(es_admin_o_delegado)
def listar_equipos(request, *args, **kwargs):
    """
    Lista equipos. Si hay campeonato_id, filtra.
    Si es DELEGADO, solo ve los suyos.
    """
    campeonato_id = _get_campeonato_id(request, kwargs)
    qs = Equipo.objects.all()
    if campeonato_id:
        qs = qs.filter(campeonato_id=campeonato_id)
    if getattr(request.user, "rol", None) == "DELEGADO":
        qs = qs.filter(delegado_id=request.user.id)
    equipos = qs.select_related("campeonato").order_by("nombre")
    camp = Campeonato.objects.filter(id=campeonato_id).first() if campeonato_id else None
    return render(request, "equipo/listar_equipos.html", {"equipos": equipos, "campeonato": camp})


@login_required
@user_passes_test(es_admin_o_delegado)
def detalle_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    form = EquipoForm(instance=equipo, user=request.user)
    return render(
        request,
        "equipo/registrar_equipo.html",
        {"form": form, "equipo": equipo, "view_mode": True},
    )


@login_required
@user_passes_test(es_admin_o_delegado)
def registrar_equipo(request):
    campeonato_id = request.GET.get('campeonato_id') or request.POST.get('campeonato_id')
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, user=request.user, campeonato_id=campeonato_id)
        if form.is_valid():
            obj = form.save()
            messages.success(request, 'Equipo registrado correctamente.')
            return redirect('listar_equipos')
        else:
            # debug no destructivo para ver por qué es inválido
            print('FORM ERRORS:', form.errors.as_json())
            messages.error(request, 'Revisa los errores del formulario.')
    else:
        form = EquipoForm(user=request.user, campeonato_id=campeonato_id)
    return render(request, 'equipo/registrar_equipo.html', {'form': form})


@login_required
@user_passes_test(es_admin_o_delegado)
def editar_equipo(request, id):
    """
    Editar equipo.
    - DELEGADO solo puede editar su propio equipo.
    - No permitir que cambien 'aprobado' desde aquí.
    """
    equipo = get_object_or_404(Equipo, id=id)

    if getattr(request.user, "rol", "").upper() == "DELEGADO" and equipo.delegado_id != request.user.id:
        return HttpResponseForbidden("No puedes editar este equipo.")

    if request.method == "POST":
        form = EquipoForm(request.POST, request.FILES, instance=equipo, user=request.user)
        if form.is_valid():
            # Mantener aprobado con el valor actual (no editable aquí para delegados)
            form.instance.aprobado = equipo.aprobado
            form.save()
            messages.success(request, "Equipo actualizado correctamente.")
            return redirect("detalle_equipo", id=equipo.id)
    else:
        form = EquipoForm(instance=equipo, user=request.user)

    return render(
        request,
        "equipo/registrar_equipo.html",
        {"form": form, "equipo": equipo, "edit_mode": True},
    )


@login_required
@user_passes_test(es_admin_o_delegado)
def pago_equipo(request, id):
    """
    Wrapper de compatibilidad: envía al flujo canónico de pagos.
    Si en tus templates existen enlaces a 'pago_equipo', esto evita romperlos.
    """
    return redirect("registrar_pago_equipo", equipo_id=id)


@login_required
@user_passes_test(es_admin_o_delegado)
def jugadores_equipo(request, id):
    """
    Mostrar jugadores del equipo SOLO si el equipo está aprobado.
    """
    equipo = get_object_or_404(Equipo, id=id)
    if not equipo.aprobado:
        messages.error(
            request,
            "El equipo no está aprobado. No puedes registrar/jugar hasta que el pago sea aprobado.",
        )
        return redirect("detalle_equipo", id=equipo.id)

    campeonato = equipo.campeonato
    deporte_nombre = campeonato.deporte.nombre.upper()

    jugadores_data = []
    for jugador in equipo.jugadores.all():
        player_stats = None
        if deporte_nombre == "FUTBOL":
            player_stats = EstadisticaJugadorFutbol.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "BASQUET":
            player_stats = EstadisticaJugadorBasquet.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "AJEDREZ":
            player_stats = EstadisticaJugadorAjedrez.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "ECUABOLY":
            player_stats = EstadisticaJugadorEcuaboly.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "PING PONG":
            player_stats = EstadisticaJugadorPingPong.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "TENIS":
            player_stats = EstadisticaJugadorTenis.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "VIDEOJUEGOS":
            player_stats = EstadisticaJugadorVideojuegos.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "FUTBOLIN":
            player_stats = EstadisticaJugadorFutbolin.objects.filter(jugador=jugador, campeonato=campeonato).first()

        jugadores_data.append({
            "jugador": jugador,
            "stats": player_stats,
            "deporte_nombre": deporte_nombre,
            "posicion": jugador.posicion,
        })

    return render(request, "equipo/jugadores_equipo.html", {"equipo": equipo, "jugadores_data": jugadores_data})


@login_required
def mis_jugadores_delegado(request):
    """
    Vista del delegado para ver SUS jugadores del equipo del campeonato activo/seleccionado.
    """
    campeonato_id = _get_campeonato_id(request)
    equipo_qs = Equipo.objects.filter(delegado_id=request.user.id)
    if campeonato_id:
        equipo_qs = equipo_qs.filter(campeonato_id=campeonato_id)
    equipo = equipo_qs.first()
    if not equipo:
        messages.error(request, "No tienes un equipo registrado en este campeonato.")
        return redirect("delegado_dashboard")

    campeonato = equipo.campeonato
    deporte_nombre = campeonato.deporte.nombre.upper()

    jugadores_data = []
    for jugador in equipo.jugadores.all():
        stats = None
        if deporte_nombre == "FUTBOL":
            stats = EstadisticaJugadorFutbol.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "BASQUET":
            stats = EstadisticaJugadorBasquet.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "AJEDREZ":
            stats = EstadisticaJugadorAjedrez.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "ECUABOLY":
            stats = EstadisticaJugadorEcuaboly.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "PING PONG":
            stats = EstadisticaJugadorPingPong.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "TENIS":
            stats = EstadisticaJugadorTenis.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "VIDEOJUEGOS":
            stats = EstadisticaJugadorVideojuegos.objects.filter(jugador=jugador, campeonato=campeonato).first()
        elif deporte_nombre == "FUTBOLIN":
            stats = EstadisticaJugadorFutbolin.objects.filter(jugador=jugador, campeonato=campeonato).first()

        jugadores_data.append({"jugador": jugador, "stats": stats, "deporte_nombre": deporte_nombre, "posicion": jugador.posicion})

    return render(
        request,
        "equipo/jugadores_equipo.html",
        {"equipo": equipo, "jugadores_data": jugadores_data, "is_delegado_view": True, "campeonato": campeonato},
    )


@login_required
@user_passes_test(es_admin_o_delegado)
def eliminar_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    if request.method == "POST":
        equipo.delete()
        messages.success(request, "Equipo eliminado correctamente.")
        return redirect("listar_equipos")
    # Confirmación ya la manejas en el template con JS
    return redirect("listar_equipos")
