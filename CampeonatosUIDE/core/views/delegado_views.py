from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import Usuario, Equipo, Pago

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