from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import Pago, Equipo
from core.forms import PagoForm, PagoDelegadoForm

class ListarPagosAdminView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('inicio')
        pagos = Pago.objects.all().order_by('-fecha_pago')
        return render(request, 'pago/listar.html', {'pagos': pagos})

class DetallePagoAdminView(LoginRequiredMixin, View):
    def get(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('inicio')
        pago = get_object_or_404(Pago, pk=pk)
        return render(request, 'pago/detalle_pago.html', {'pago': pago})

class AprobarPagoAdminView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('inicio')
        pago = get_object_or_404(Pago, pk=pk)
        if pago.estado == 'PENDIENTE':
            pago.estado = 'APROBADO'
            pago.observacion_admin = request.POST.get('observacion_admin', '')
            pago.save()
            messages.success(request, f'Pago del equipo {pago.equipo.nombre} aprobado correctamente.')
        else:
            messages.warning(request, f'El pago del equipo {pago.equipo.nombre} ya está en estado {pago.estado}.')
        return redirect('detalle_pago_admin', pk=pk)

class RechazarPagoAdminView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('inicio')
        pago = get_object_or_404(Pago, pk=pk)
        if pago.estado == 'PENDIENTE' or pago.estado == 'APROBADO':
            pago.estado = 'RECHAZADO'
            pago.observacion_admin = request.POST.get('observacion_admin', '')
            pago.save()
            messages.success(request, f'Pago del equipo {pago.equipo.nombre} rechazado correctamente.')
        else:
            messages.warning(request, f'El pago del equipo {pago.equipo.nombre} ya está en estado {pago.estado}.')
        return redirect('detalle_pago_admin', pk=pk)

class RegistrarPagoAdminView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('inicio')
        form = PagoForm()
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'crear'})

    def post(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('inicio')
        form = PagoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pago registrado correctamente por el administrador.')
            return redirect('listar_pagos_admin')
        messages.error(request, "Error al registrar el pago. Por favor, revisa los campos.")
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'crear'})

class EditarPagoAdminView(LoginRequiredMixin, View):
    def get(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('inicio')
        pago = get_object_or_404(Pago, pk=pk)
        form = PagoForm(instance=pago)
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'editar', 'pago': pago})

    def post(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('inicio')
        pago = get_object_or_404(Pago, pk=pk)
        form = PagoForm(request.POST, request.FILES, instance=pago)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pago actualizado correctamente por el administrador.')
            return redirect('listar_pagos_admin')
        messages.error(request, "Error al actualizar el pago. Por favor, revisa los campos.")
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'editar', 'pago': pago})

class EliminarPagoAdminView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('inicio')
        pago = get_object_or_404(Pago, pk=pk)
        pago.delete()
        messages.success(request, 'Pago eliminado correctamente por el administrador.')
        return redirect('listar_pagos_admin')

class RegistrarPagoParaEquipoAdminView(LoginRequiredMixin, View):
    def get(self, request, equipo_id):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('inicio')
        equipo = get_object_or_404(Equipo, pk=equipo_id)
        form = PagoForm(initial={'equipo': equipo})
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'crear', 'equipo': equipo})

    def post(self, request, equipo_id):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('inicio')
        equipo = get_object_or_404(Equipo, pk=equipo_id)
        form = PagoForm(request.POST, request.FILES)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.equipo = equipo
            pago.save()
            messages.success(request, f'Pago registrado correctamente para el equipo {equipo.nombre}.')
            return redirect('detalle_equipo', id=equipo.id)
        messages.error(request, "Error al registrar el pago. Por favor, revisa los campos.")
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'crear', 'equipo': equipo})

class RegistrarPagoDelegadoView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('inicio')
        
        try:
            equipo = Equipo.objects.get(delegado=request.user)
        except Equipo.DoesNotExist:
            messages.warning(request, "Debes tener un equipo registrado para poder registrar un pago.")
            return redirect('delegado_dashboard')
        
        pago_existente = Pago.objects.filter(equipo=equipo).first()
        
        if pago_existente and not request.GET.get('edit_mode'):
            # Si existe un pago y no se ha solicitado el modo edición, mostrar resumen
            return render(request, 'pago/pago_existente.html', {'pago': pago_existente, 'equipo': equipo})
        else:
            # Si no existe pago, o si se solicitó el modo edición, mostrar el formulario
            form = PagoDelegadoForm(instance=pago_existente) if pago_existente else PagoDelegadoForm(initial={'equipo': equipo})
            return render(request, 'pago/registrar.html', {'form': form, 'equipo': equipo, 'pago_existente': pago_existente})

    def post(self, request):
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('inicio')
        
        try:
            equipo = Equipo.objects.get(delegado=request.user)
        except Equipo.DoesNotExist:
            messages.warning(request, "Debes tener un equipo registrado para poder registrar un pago.")
            return redirect('delegado_dashboard')
        
        pago_existente = Pago.objects.filter(equipo=equipo).first()
        
        if pago_existente:
            form = PagoDelegadoForm(request.POST, request.FILES, instance=pago_existente)
        else:
            form = PagoDelegadoForm(request.POST, request.FILES)
        
        if form.is_valid():
            pago = form.save(commit=False)
            pago.equipo = equipo
            pago.save()
            messages.success(request, 'Pago registrado/actualizado correctamente.')
            return redirect('detalle_pago_delegado')
        else:
            messages.error(request, "Error al registrar/actualizar el pago. Por favor, revisa los campos.")
            return render(request, 'pago/registrar.html', {'form': form, 'equipo': equipo, 'pago_existente': pago_existente})

class DetallePagoDelegadoView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('inicio')
        
        try:
            equipo = Equipo.objects.get(delegado=request.user)
            pago = Pago.objects.get(equipo=equipo)
        except (Equipo.DoesNotExist, Pago.DoesNotExist):
            messages.info(request, "Aún no has registrado un pago para tu equipo.")
            return redirect('registrar_pago_delegado') # Redirigir a la página de registro de pago
        
        return render(request, 'pago/detalle_pago_delegado.html', {'pago': pago})

class EliminarPagoDelegadoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('inicio')
        
        pago = get_object_or_404(Pago, pk=pk)
        
        # Asegurarse de que el delegado solo pueda eliminar su propio pago
        try:
            equipo_delegado = Equipo.objects.get(delegado=request.user)
            if pago.equipo != equipo_delegado:
                messages.error(request, "No tienes permiso para eliminar este pago.")
                return redirect('detalle_pago_delegado')
        except Equipo.DoesNotExist:
            messages.error(request, "No tienes un equipo asociado para eliminar pagos.")
            return redirect('delegado_dashboard')
            
        pago.delete()
        messages.success(request, 'Pago eliminado correctamente.')
        return redirect('registrar_pago_delegado') # Redirigir a la página de registro de pago después de eliminar