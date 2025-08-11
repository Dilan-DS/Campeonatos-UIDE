from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from core.models import Usuario, Equipo, Pago, Jugador

class ListarDelegadosView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        delegados = Usuario.objects.filter(rol='DELEGADO').order_by('username')
        return render(request, 'delegado/listar.html', {'delegados': delegados})

class DelegadoDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        
        campeonato_id = request.GET.get('campeonato_id') or request.POST.get('campeonato_id') or request.session.get('campeonato_id')
        if campeonato_id:
            request.session['campeonato_id'] = int(campeonato_id)

        qs = Equipo.objects.filter(delegado_id=request.user.id)
        if campeonato_id:
            qs = qs.filter(campeonato_id=campeonato_id)
        equipo = qs.first()

        pago = None
        if equipo:
            pago = Pago.objects.filter(equipo=equipo).first()

        return render(request, 'dashboard/delegado.html', {'equipo': equipo, 'pago': pago})

class ListarJugadoresParaEquipoView(LoginRequiredMixin, View):
    def get(self, request):
        from core.models import Equipo, Pago, Usuario, Jugador, Campeonato
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        # campeonato actual desde kwargs/GET/POST/session/activo
        campeonato_id = (
            request.GET.get('campeonato_id')
            or request.POST.get('campeonato_id')
            or request.session.get('campeonato_id')
        )
        if not campeonato_id:
            camp = Campeonato.objects.filter(activo='SI').order_by('-fecha_inicio').first()
            campeonato_id = camp.id if camp else None
        if campeonato_id:
            request.session['campeonato_id'] = int(campeonato_id)
        
        equipo_delegado = Equipo.objects.filter(delegado_id=request.user.id)
        if campeonato_id:
            equipo_delegado = equipo_delegado.filter(campeonato_id=campeonato_id)
        equipo_delegado = equipo_delegado.first()

        if not equipo_delegado:
            messages.error(request, "No tienes un equipo registrado en este campeonato.")
            return redirect('delegado_dashboard')

        pago_equipo = Pago.objects.filter(equipo=equipo_delegado).first()
        if not pago_equipo or pago_equipo.estado != 'APROBADO':
            messages.warning(request, "Tu equipo debe tener el pago aprobado para gestionar jugadores.")
            return redirect('delegado_dashboard')

        jugadores_disponibles = Usuario.objects.filter(rol='JUGADOR', genero=equipo_delegado.genero).order_by('username')
        jugadores_data = []
        for jugador_usuario in jugadores_disponibles:
            jugador_obj = Jugador.objects.filter(usuario=jugador_usuario).first()
            ya_inscrito = bool(jugador_obj and jugador_obj.equipo_id)
            estado_inscripcion = f"Ya inscrito en: {jugador_obj.equipo.nombre}" if ya_inscrito else "Disponible"
            jugadores_data.append({
                'usuario': jugador_usuario,
                'ya_inscrito': ya_inscrito,
                'estado_inscripcion': estado_inscripcion,
                'es_mi_jugador': (jugador_obj and jugador_obj.equipo_id == equipo_delegado.id),
            })
        
        return render(request, 'jugador/listar_jugadores.html', {
            'jugadores_data': jugadores_data,
            'equipo_delegado': equipo_delegado,
            'pago_aprobado': True,
        })

class AgregarJugadorAEquipoView(LoginRequiredMixin, View):
    def post(self, request, jugador_usuario_id):
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')

        campeonato_id = request.GET.get('campeonato_id') or request.POST.get('campeonato_id') or request.session.get('campeonato_id')
        if campeonato_id:
            request.session['campeonato_id'] = int(campeonato_id)

        qs = Equipo.objects.filter(delegado_id=request.user.id)
        if campeonato_id:
            qs = qs.filter(campeonato_id=campeonato_id)
        equipo_delegado = qs.first()

        if not equipo_delegado:
            messages.error(request, "No tienes un equipo registrado en este campeonato.")
            return redirect('delegado_dashboard')

        pago_equipo = Pago.objects.filter(equipo=equipo_delegado).first()

        if not pago_equipo or pago_equipo.estado != 'APROBADO':
            messages.error(request, "Tu equipo debe tener el pago aprobado para agregar jugadores.")
            return redirect('listar_jugadores_para_equipo')

        jugador_usuario = get_object_or_404(Usuario, id=jugador_usuario_id, rol='JUGADOR')

        # Intentar encontrar el objeto Jugador para el Usuario seleccionado
        jugador_existente = Jugador.objects.filter(usuario=jugador_usuario).first()

        # Si el objeto Jugador no existe, significa que el usuario no completó el registro como jugador
        if not jugador_existente:
            messages.error(request, f"El usuario {jugador_usuario.username} no tiene un registro de jugador completo y no puede ser agregado a un equipo.")
            return redirect('listar_jugadores_para_equipo')

        # Verificar si el jugador ya está en otro equipo
        if jugador_existente.equipo:
            messages.warning(request, f"{jugador_usuario.username} ya está inscrito en el equipo {jugador_existente.equipo.nombre}.")
            return redirect('listar_jugadores_para_equipo')

        # Verificar si el equipo ya alcanzó el máximo de jugadores
        if equipo_delegado.jugadores.count() >= equipo_delegado.campeonato.max_jugadores_por_equipo:
            messages.error(request, f"Tu equipo ya tiene el máximo de jugadores permitidos ({equipo_delegado.campeonato.max_jugadores_por_equipo}).")
            return redirect('listar_jugadores_para_equipo')

        # Asignar el equipo al jugador existente y guardar
        jugador_existente.equipo = equipo_delegado
        jugador_existente.save()
        messages.success(request, f"{jugador_usuario.username} ha sido agregado a tu equipo.")
        return redirect('listar_jugadores_para_equipo')