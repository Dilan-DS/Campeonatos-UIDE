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
            return redirect('inicio')
        delegados = Usuario.objects.filter(rol='DELEGADO').order_by('username')
        return render(request, 'delegado/listar.html', {'delegados': delegados})

class DelegadoDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('inicio')
        
        equipo = None
        pago = None
        try:
            equipo = Equipo.objects.get(delegado=request.user)
            # Intentar obtener el pago asociado al equipo
            pago = Pago.objects.filter(equipo=equipo).first()
        except Equipo.DoesNotExist:
            pass # No hay equipo registrado para este delegado

        return render(request, 'dashboard/delegado.html', {'equipo': equipo, 'pago': pago})

class ListarJugadoresParaEquipoView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('inicio')

        try:
            equipo_delegado = Equipo.objects.get(delegado=request.user)
            pago_equipo = Pago.objects.filter(equipo=equipo_delegado).first()
            
            if not pago_equipo or pago_equipo.estado != 'APROBADO':
                messages.warning(request, "Tu equipo debe tener el pago aprobado para gestionar jugadores.")
                return redirect('delegado_dashboard') # Redirigir a un lugar seguro, o mostrar un mensaje en la misma página
            
            # Obtener todos los usuarios con rol JUGADOR que coincidan con el género del equipo
            jugadores_disponibles = Usuario.objects.filter(
                rol='JUGADOR',
                genero=equipo_delegado.genero
            ).order_by('username')

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
                    'es_mi_jugador': (jugador_obj and jugador_obj.equipo == equipo_delegado)
                })
            
            context = {
                'jugadores_data': jugadores_data,
                'equipo_delegado': equipo_delegado,
                'pago_aprobado': True, # Ya se verificó arriba
            }
            return render(request, 'jugador/listar_jugadores.html', context)

        except Equipo.DoesNotExist:
            messages.error(request, "No tienes un equipo registrado. Registra uno primero.")
            return redirect('delegado_dashboard') # O a la página de registro de equipo

class AgregarJugadorAEquipoView(LoginRequiredMixin, View):
    def post(self, request, jugador_usuario_id):
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('inicio')

        try:
            equipo_delegado = Equipo.objects.get(delegado=request.user)
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
            messages.success(request, f"{jugador_usuario.username} ha sido agregado a tu equipo.")
            return redirect('listar_jugadores_para_equipo')

        except Equipo.DoesNotExist:
            messages.error(request, "No tienes un equipo registrado.")
            return redirect('delegado_dashboard')
        except Exception as e:
            messages.error(request, f"Ocurrió un error al agregar al jugador: {e}")
            return redirect('listar_jugadores_para_equipo')