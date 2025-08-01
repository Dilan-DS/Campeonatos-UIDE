from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import Usuario, Equipo

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
        try:
            equipo = Equipo.objects.get(delegado=request.user)
        except Equipo.DoesNotExist:
            pass # No hay equipo registrado para este delegado

        return render(request, 'dashboard/delegado.html', {'equipo': equipo})