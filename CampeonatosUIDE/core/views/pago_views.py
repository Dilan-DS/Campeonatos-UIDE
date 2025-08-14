import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import Pago, Equipo, CodigoQR
from core.forms import PagoForm, PagoDelegadoForm
from django.urls import reverse
from django import forms
from django.core.serializers.json import DjangoJSONEncoder
import json
from django import forms
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.core.paginator import Paginator 

class ListarPagosAdminView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        pagos = Pago.objects.all().order_by('-fecha_pago')
        return render(request, 'pago/listar.html', {'pagos': pagos})

class DetallePagoAdminView(LoginRequiredMixin, View):
    def get(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        pago = get_object_or_404(Pago, pk=pk)
        return render(request, 'pago/detalle_pago.html', {'pago': pago})

class AprobarPagoAdminView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
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
            return redirect('vista_inicio')
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
            return redirect('vista_inicio')
        form = PagoForm()
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'crear'})

    def post(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
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
            return redirect('vista_inicio')
        pago = get_object_or_404(Pago, pk=pk)
        form = PagoForm(instance=pago)
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'editar', 'pago': pago})

    def post(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
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
            return redirect('vista_inicio')
        pago = get_object_or_404(Pago, pk=pk)
        pago.delete()
        messages.success(request, 'Pago eliminado correctamente por el administrador.')
        return redirect('listar_pagos_admin')

class RegistrarPagoParaEquipoAdminView(LoginRequiredMixin, View):
    def get(self, request, equipo_id):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        equipo = get_object_or_404(Equipo, pk=equipo_id)
        form = PagoForm(initial={'equipo': equipo})
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'crear', 'equipo': equipo})

    def post(self, request, equipo_id):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
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

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
import json

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
import json

import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import Pago, Equipo, CodigoQR
from core.forms import PagoForm, PagoDelegadoForm
from django.urls import reverse


class ListarPagosAdminView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        pagos = Pago.objects.all().order_by('-fecha_pago')
        return render(request, 'pago/listar.html', {'pagos': pagos})

class DetallePagoAdminView(LoginRequiredMixin, View):
    def get(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        pago = get_object_or_404(Pago, pk=pk)
        return render(request, 'pago/detalle_pago.html', {'pago': pago})

class AprobarPagoAdminView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
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
            return redirect('vista_inicio')
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
            return redirect('vista_inicio')
        form = PagoForm()
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'crear'})

    def post(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
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
            return redirect('vista_inicio')
        pago = get_object_or_404(Pago, pk=pk)
        form = PagoForm(instance=pago)
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'editar', 'pago': pago})

    def post(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
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
            return redirect('vista_inicio')
        pago = get_object_or_404(Pago, pk=pk)
        pago.delete()
        messages.success(request, 'Pago eliminado correctamente por el administrador.')
        return redirect('listar_pagos_admin')

class RegistrarPagoParaEquipoAdminView(LoginRequiredMixin, View):
    def get(self, request, equipo_id):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        equipo = get_object_or_404(Equipo, pk=equipo_id)
        form = PagoForm(initial={'equipo': equipo})
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'crear', 'equipo': equipo})

    def post(self, request, equipo_id):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
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
    def get(self, request, *args, **kwargs):
        equipo_id = kwargs.get("equipo_id") or request.GET.get("equipo_id")
        equipo = None
        if equipo_id:
            equipo = get_object_or_404(Equipo, pk=equipo_id)

        pago_existente = None
        equipo_nombre = ""
        
        es_delegado = getattr(request.user, "rol", "") == "DELEGADO"
        
        if not equipo and es_delegado:
            qs_equipo = Equipo.objects.filter(delegado=request.user)
            if qs_equipo.exists():
                equipo = qs_equipo.first()

        if equipo:
            equipo_nombre = equipo.nombre
            pago_existente = Pago.objects.filter(equipo=equipo).first()

        form = PagoDelegadoForm(instance=pago_existente) if pago_existente else PagoDelegadoForm(initial={'equipo': equipo})

        # después de crear el form (GET y POST)
        if "equipo" in form.fields:
            if getattr(request.user, "rol", "") == "DELEGADO":
                form.fields["equipo"].queryset = Equipo.objects.filter(delegado=request.user)
            else:
                form.fields["equipo"].queryset = Equipo.objects.all()

        ctx = {
            "form": form,
            "equipo": equipo,
            "pago_existente": pago_existente,
            "equipo_nombre": equipo_nombre,
        }

        qs_qr = CodigoQR.visibles_para_delegados()
        if "codigo_qr" in form.fields:
            form.fields["codigo_qr"].queryset = qs_qr
        ocultar_select_qr = False
        if getattr(request.user, "rol", "") == "DELEGADO":
            form.fields["codigo_qr"].widget = forms.HiddenInput()
            ocultar_select_qr = True
            principal = qs_qr.first()
            if principal and not (form.instance and form.instance.codigo_qr_id):
                form.initial = {**getattr(form, "initial", {}), "codigo_qr": principal.pk}
        qr_principal = qs_qr.first()  # NUEVO
        qr_catalog = {qr.pk: qr.to_dict() for qr in qs_qr}
        ctx.update({
            "ocultar_select_qr": ocultar_select_qr,
            "qr_catalog_json": json.dumps(qr_catalog, cls=DjangoJSONEncoder),
            "qr_principal": qr_principal,  # ← NUEVO
        })
        
        return render(request, "pago/registrar.html", ctx)

    import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from core.models import Pago, Equipo, CodigoQR
from core.forms import PagoForm, PagoDelegadoForm
from django.urls import reverse


class ListarPagosAdminView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        pagos = Pago.objects.all().order_by('-fecha_pago')
        return render(request, 'pago/listar.html', {'pagos': pagos})

class DetallePagoAdminView(LoginRequiredMixin, View):
    def get(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        pago = get_object_or_404(Pago, pk=pk)
        return render(request, 'pago/detalle_pago.html', {'pago': pago})

class AprobarPagoAdminView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
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
            return redirect('vista_inicio')
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
            return redirect('vista_inicio')
        form = PagoForm()
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'crear'})

    def post(self, request):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
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
            return redirect('vista_inicio')
        pago = get_object_or_404(Pago, pk=pk)
        form = PagoForm(instance=pago)
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'editar', 'pago': pago})

    def post(self, request, pk):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
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
            return redirect('vista_inicio')
        pago = get_object_or_404(Pago, pk=pk)
        pago.delete()
        messages.success(request, 'Pago eliminado correctamente por el administrador.')
        return redirect('listar_pagos_admin')

class RegistrarPagoParaEquipoAdminView(LoginRequiredMixin, View):
    def get(self, request, equipo_id):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        equipo = get_object_or_404(Equipo, pk=equipo_id)
        form = PagoForm(initial={'equipo': equipo})
        return render(request, 'pago/registrar_admin.html', {'form': form, 'modo': 'crear', 'equipo': equipo})

    def post(self, request, equipo_id):
        if not request.user.rol == 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
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

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
import json

from django import forms
from django.core.serializers.json import DjangoJSONEncoder
import json

class RegistrarPagoDelegadoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        equipo_id = kwargs.get("equipo_id") or request.GET.get("equipo_id")
        equipo = None
        if equipo_id:
            equipo = get_object_or_404(Equipo, pk=equipo_id)

        pago_existente = None
        equipo_nombre = ""
        
        es_delegado = getattr(request.user, "rol", "") == "DELEGADO"
        
        if not equipo and es_delegado:
            qs_equipo = Equipo.objects.filter(delegado=request.user)
            if qs_equipo.exists():
                equipo = qs_equipo.first()

        if equipo:
            equipo_nombre = equipo.nombre
            pago_existente = Pago.objects.filter(equipo=equipo).first()

        form = PagoDelegadoForm(instance=pago_existente) if pago_existente else PagoDelegadoForm(initial={'equipo': equipo})

        # después de crear el form (GET y POST)
        if "equipo" in form.fields:
            if getattr(request.user, "rol", "") == "DELEGADO":
                form.fields["equipo"].queryset = Equipo.objects.filter(delegado=request.user)
            else:
                form.fields["equipo"].queryset = Equipo.objects.all()

        ctx = {
            "form": form,
            "equipo": equipo,
            "pago_existente": pago_existente,
            "equipo_nombre": equipo_nombre,
        }

        qs_qr = CodigoQR.visibles_para_delegados()
        if "codigo_qr" in form.fields:
            form.fields["codigo_qr"].queryset = qs_qr
        ocultar_select_qr = False
        if getattr(request.user, "rol", "") == "DELEGADO":
            form.fields["codigo_qr"].widget = forms.HiddenInput()
            ocultar_select_qr = True
            principal = qs_qr.first()
            if principal and not (form.instance and form.instance.codigo_qr_id):
                form.initial = {**getattr(form, "initial", {}), "codigo_qr": principal.pk}
        qr_principal = qs_qr.first()  # NUEVO
        qr_catalog = {qr.pk: qr.to_dict() for qr in qs_qr}
        ctx.update({
            "ocultar_select_qr": ocultar_select_qr,
            "qr_catalog_json": json.dumps(qr_catalog, cls=DjangoJSONEncoder),
            "qr_principal": qr_principal,  # ← NUEVO
        })
        
        return render(request, "pago/registrar.html", ctx)

    def post(self, request, *args, **kwargs):
        equipo_id = kwargs.get("equipo_id") or request.POST.get("equipo")
        equipo = get_object_or_404(Equipo, pk=equipo_id) if equipo_id else None
        es_delegado = getattr(request.user, "rol", "") == "DELEGADO"
        # Si no llegó equipo y es delegado, toma su primer equipo
        if not equipo and es_delegado:
            equipo = Equipo.objects.filter(delegado=request.user).first()
        pago_existente = Pago.objects.filter(equipo=equipo).first() if equipo else None
        # *** CLAVE: completar datos ANTES de validar ***
        data = request.POST.copy()
        # Forzar equipo en el POST si lo determinamos por URL/rol
        if equipo:
            data["equipo"] = str(equipo.pk)
        # Si es transferencia y el delegado no envió codigo_qr, poner el principal
        if data.get("metodo") == "TRANSFERENCIA" and not data.get("codigo_qr"):
            principal = CodigoQR.visibles_para_delegados().first()
            if principal:
                data["codigo_qr"] = str(principal.pk)
        form = PagoDelegadoForm(data, request.FILES, instance=pago_existente)
        # Limitar queryset del campo equipo según rol (para validación)
        if "equipo" in form.fields:
            if es_delegado:
                form.fields["equipo"].queryset = Equipo.objects.filter(delegado=request.user)
            else:
                form.fields["equipo"].queryset = Equipo.objects.all()
        if form.is_valid():
            pago = form.save(commit=False)
            # Normalizar: si no es transferencia, limpiar codigo_qr
            if pago.metodo != 'TRANSFERENCIA':
                pago.codigo_qr = None
            # Asegurar el equipo en el modelo
            if equipo:
                pago.equipo = equipo
            pago.save()
            messages.success(request, 'Pago registrado/actualizado correctamente.')
            return redirect('detalle_pago_delegado')
        # --- Si no es válido, reconstruir contexto como ya lo haces ---
        qs_qr = CodigoQR.visibles_para_delegados()
        if "codigo_qr" in form.fields:
            form.fields["codigo_qr"].queryset = qs_qr
        ocultar_select_qr = False
        if es_delegado:
            form.fields["codigo_qr"].widget = forms.HiddenInput()
            ocultar_select_qr = True
            principal = qs_qr.first()
            if principal and not (form.instance and form.instance.codigo_qr_id):
                form.initial = {**getattr(form, "initial", {}), "codigo_qr": principal.pk}
        qr_catalog = {qr.pk: qr.to_dict() for qr in qs_qr}
        ctx = {
            "form": form,
            "equipo": equipo,
            "pago_existente": pago_existente,
            "equipo_nombre": equipo.nombre if equipo else "",
            "ocultar_select_qr": ocultar_select_qr,
            "qr_catalog_json": json.dumps(qr_catalog, cls=DjangoJSONEncoder),
        }
        messages.error(request, "Error al registrar/actualizar el pago. Revisa los campos.")
        return render(request, "pago/registrar.html", ctx)

class DetallePagoDelegadoView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        
        campeonato_id = (request.GET.get('campeonato_id') or request.POST.get('campeonato_id') or request.session.get('campeonato_id'))
        if campeonato_id:
            request.session['campeonato_id'] = int(campeonato_id)
        qs_equipo = Equipo.objects.filter(delegado_id=request.user.id)
        if campeonato_id:
            qs_equipo = qs_equipo.filter(campeonato_id=campeonato_id)
        equipo = qs_equipo.first()
        if not equipo:
            messages.error(request, "No tienes un equipo registrado en este campeonato.")
            return redirect('delegado_dashboard')

        try:
            pago = Pago.objects.get(equipo=equipo)
        except Pago.DoesNotExist:
            messages.info(request, "Aún no has registrado un pago para tu equipo.")
            cid = (request.GET.get('campeonato_id') or request.POST.get('campeonato_id') or request.session.get('campeonato_id'))
            url = reverse('registrar_pago_delegado')
            return redirect(f"{url}?campeonato_id={cid}") if cid else redirect(url)
        
        return render(request, 'pago/detalle_pago_delegado.html', {'pago': pago})

class EliminarPagoDelegadoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
        
        pago = get_object_or_404(Pago, pk=pk)
        
        campeonato_id = (request.GET.get('campeonato_id') or request.POST.get('campeonato_id') or request.session.get('campeonato_id'))
        if campeonato_id:
            request.session['campeonato_id'] = int(campeonato_id)
        qs_equipo = Equipo.objects.filter(delegado_id=request.user.id)
        if campeonato_id:
            qs_equipo = qs_equipo.filter(campeonato_id=campeonato_id)
        equipo_delegado = qs_equipo.first()

        if not equipo_delegado:
            messages.error(request, "No tienes un equipo registrado en este campeonato.")
            return redirect('delegado_dashboard')
            
        if pago.equipo != equipo_delegado:
            messages.error(request, "No tienes permiso para eliminar este pago.")
            return redirect('detalle_pago_delegado')
            
        pago.delete()
        messages.success(request, 'Pago eliminado correctamente.')
        cid = (request.GET.get('campeonato_id') or request.POST.get('campeonato_id') or request.session.get('campeonato_id'))
        url = reverse('registrar_pago_delegado')
        return redirect(f"{url}?campeonato_id={cid}") if cid else redirect(url)


class CambiarEstadoPagoAdminView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if getattr(request.user, 'rol', '') != 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
        
        pago = get_object_or_404(Pago, pk=pk)
        nuevo_estado = request.POST.get('estado')
        validos = {'PENDIENTE', 'APROBADO', 'RECHAZADO'}

        if nuevo_estado not in validos:
            messages.error(request, "Estado no válido.")
        else:
            if pago.estado != nuevo_estado:
                pago.estado = nuevo_estado
                obs = request.POST.get('observacion_admin', '') # Default to empty string if not provided
                pago.observacion_admin = obs # Assign directly
                pago.save()
                messages.success(request, f"Estado actualizado a {nuevo_estado}.")
            else:
                messages.info(request, "Sin cambios.")
        
        next_url = request.POST.get('next') or reverse('listar_pagos_admin')
        return redirect(next_url)

    def post(self, request, *args, **kwargs):
        equipo_id = kwargs.get("equipo_id") or request.POST.get("equipo")
        equipo = None
        if equipo_id:
            equipo = get_object_or_404(Equipo, pk=equipo_id)

        es_delegado = getattr(request.user, "rol", "") == "DELEGADO"
        
        if not equipo and es_delegado:
            qs_equipo = Equipo.objects.filter(delegado=request.user)
            if qs_equipo.exists():
                equipo = qs_equipo.first()

        pago_existente = Pago.objects.filter(equipo=equipo).first() if equipo else None
        form = PagoDelegadoForm(request.POST, request.FILES, instance=pago_existente)

        if form.is_valid():
            pago = form.save(commit=False)
            if pago.metodo != 'TRANSFERENCIA':
                pago.codigo_qr = None
            else:
                if es_delegado and not pago.codigo_qr_id:
                    principal = CodigoQR.visibles_para_delegados().first()
                    if principal:
                        pago.codigo_qr = principal
            if equipo:
                pago.equipo = equipo
            pago.save()
            messages.success(request, 'Pago registrado/actualizado correctamente.')
            return redirect('detalle_pago_delegado')
        else:
            ctx = {
                "form": form,
                "equipo": equipo,
                "pago_existente": pago_existente,
                "equipo_nombre": equipo.nombre if equipo else "",
            }
            
            qs_qr = CodigoQR.visibles_para_delegados()
            if "codigo_qr" in form.fields:
                form.fields["codigo_qr"].queryset = qs_qr
            ocultar_select_qr = False
            if getattr(request.user, "rol", "") == "DELEGADO":
                form.fields["codigo_qr"].widget = forms.HiddenInput()
                ocultar_select_qr = True
                principal = qs_qr.first()
                if principal and not (form.instance and form.instance.codigo_qr_id):
                    form.initial = {**getattr(form, "initial", {}), "codigo_qr": principal.pk}
            qr_principal = qs_qr.first()  # NUEVO
            qr_catalog = {qr.pk: qr.to_dict() for qr in qs_qr}
            ctx.update({
                "ocultar_select_qr": ocultar_select_qr,
                "qr_catalog_json": json.dumps(qr_catalog, cls=DjangoJSONEncoder),
                "qr_principal": qr_principal,  # ← NUEVO
            })

            messages.error(request, "Error al registrar/actualizar el pago. Revisa los campos.")
            return render(request, "pago/registrar.html", ctx)

class DetallePagoDelegadoView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('vista_inicio')
        
        campeonato_id = (request.GET.get('campeonato_id') or request.POST.get('campeonato_id') or request.session.get('campeonato_id'))
        if campeonato_id:
            request.session['campeonato_id'] = int(campeonato_id)
        qs_equipo = Equipo.objects.filter(delegado_id=request.user.id)
        if campeonato_id:
            qs_equipo = qs_equipo.filter(campeonato_id=campeonato_id)
        equipo = qs_equipo.first()
        if not equipo:
            messages.error(request, "No tienes un equipo registrado en este campeonato.")
            return redirect('delegado_dashboard')

        try:
            pago = Pago.objects.get(equipo=equipo)
        except Pago.DoesNotExist:
            messages.info(request, "Aún no has registrado un pago para tu equipo.")
            cid = (request.GET.get('campeonato_id') or request.POST.get('campeonato_id') or request.session.get('campeonato_id'))
            url = reverse('registrar_pago_delegado')
            return redirect(f"{url}?campeonato_id={cid}") if cid else redirect(url)
        
        return render(request, 'pago/detalle_pago_delegado.html', {'pago': pago})

class EliminarPagoDelegadoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.rol == 'DELEGADO':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
        
        pago = get_object_or_404(Pago, pk=pk)
        
        campeonato_id = (request.GET.get('campeonato_id') or request.POST.get('campeonato_id') or request.session.get('campeonato_id'))
        if campeonato_id:
            request.session['campeonato_id'] = int(campeonato_id)
        qs_equipo = Equipo.objects.filter(delegado_id=request.user.id)
        if campeonato_id:
            qs_equipo = qs_equipo.filter(campeonato_id=campeonato_id)
        equipo_delegado = qs_equipo.first()

        if not equipo_delegado:
            messages.error(request, "No tienes un equipo registrado en este campeonato.")
            return redirect('delegado_dashboard')
            
        if pago.equipo != equipo_delegado:
            messages.error(request, "No tienes permiso para eliminar este pago.")
            return redirect('detalle_pago_delegado')
            
        pago.delete()
        messages.success(request, 'Pago eliminado correctamente.')
        cid = (request.GET.get('campeonato_id') or request.POST.get('campeonato_id') or request.session.get('campeonato_id'))
        url = reverse('registrar_pago_delegado')
        return redirect(f"{url}?campeonato_id={cid}") if cid else redirect(url)


class CambiarEstadoPagoAdminView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if getattr(request.user, 'rol', '') != 'ADMIN':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('vista_inicio')
        
        pago = get_object_or_404(Pago, pk=pk)
        nuevo_estado = request.POST.get('estado')
        validos = {'PENDIENTE', 'APROBADO', 'RECHAZADO'}

        if nuevo_estado not in validos:
            messages.error(request, "Estado no válido.")
        else:
            if pago.estado != nuevo_estado:
                pago.estado = nuevo_estado
                obs = request.POST.get('observacion_admin', '') # Default to empty string if not provided
                pago.observacion_admin = obs # Assign directly
                pago.save()
                messages.success(request, f"Estado actualizado a {nuevo_estado}.")
            else:
                messages.info(request, "Sin cambios.")
        
        next_url = request.POST.get('next') or reverse('listar_pagos_admin')
        return redirect(next_url)

class ListarPagosDelegadoView(LoginRequiredMixin, View):
    def get(self, request):
        if getattr(request.user, "rol", "") != "DELEGADO":
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect("vista_inicio")

        qs = Pago.objects.filter(
            equipo__delegado=request.user
        ).select_related("equipo", "codigo_qr").order_by("-fecha_pago", "-id")

        # Filtro opcional por campeonato (mantén compat con lo que ya usan)
        campeonato_id = request.GET.get("campeonato_id") or request.session.get("campeonato_id")
        if campeonato_id:
            try:
                request.session["campeonato_id"] = int(campeonato_id)
                qs = qs.filter(equipo__campeonato_id=campeonato_id)
            except ValueError:
                pass

        paginator = Paginator(qs, 9)
        page_obj = paginator.get_page(request.GET.get("page"))

        ctx = {
            "pagos": page_obj,
            "page_obj": page_obj,
            "campeonato_id": campeonato_id,
        }
        return render(request, "pago/mis_pagos.html", ctx)