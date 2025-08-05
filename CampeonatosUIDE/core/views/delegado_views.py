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

            # Verificar si el jugador ya está en algún equipo
            if Jugador.objects.filter(usuario=jugador_usuario).exists():
                messages.warning(request, f"{jugador_usuario.username} ya está inscrito en otro equipo.")
                return redirect('listar_jugadores_para_equipo')
            
            # Verificar si el equipo ya alcanzó el máximo de jugadores
            if equipo_delegado.jugadores.count() >= equipo_delegado.campeonato.max_jugadores_por_equipo:
                messages.error(request, f"Tu equipo ya tiene el máximo de jugadores permitidos ({equipo_delegado.campeonato.max_jugadores_por_equipo}).")
                return redirect('listar_jugadores_para_equipo')

            # Crear el objeto Jugador y asignarlo al equipo
            # Asignar un número de camiseta. Podrías tener una lógica más sofisticada aquí.
            # Por ahora, asignaremos el siguiente número disponible o 1 si no hay jugadores.
            next_camiseta_number = 1
            if equipo_delegado.jugadores.exists():
                last_player = equipo_delegado.jugadores.order_by('-numero_camiseta').first()
                next_camiseta_number = last_player.numero_camiseta + 1

            Jugador.objects.create(
                usuario=jugador_usuario,
                equipo=equipo_delegado,
                numero_camiseta=jugador_usuario.numero_camiseta, # Use numero_camiseta from Usuario
                posicion=jugador_usuario.posicion, # Use posicion from Usuario
                edad=18 # Assuming a default age or that it's set elsewhere
            )
            messages.success(request, f"{jugador_usuario.username} ha sido agregado a tu equipo.")
            return redirect('listar_jugadores_para_equipo')

        except Equipo.DoesNotExist:
            messages.error(request, "No tienes un equipo registrado.")
            return redirect('delegado_dashboard')
        except Exception as e:
            messages.error(request, f"Ocurrió un error al agregar al jugador: {e}")
            return redirect('listar_jugadores_para_equipo')