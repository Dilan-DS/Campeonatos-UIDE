from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from core.models import Pago, CodigoQR
from core.forms import PagoForm  # Asumo que tienes un formulario PagoForm

class listar_pagos(View):
    def get(self, request):
        pagos = Pago.objects.all()
        return render(request, 'pago/listar.html', {'pagos': pagos})

class registrar_pago(View):
    def get(self, request):
        form = PagoForm()
        return render(request, 'pago/registrar.html', {
            'form': form,
            'modo': 'crear'
        })

    def post(self, request):
        form = PagoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pago registrado correctamente')
            return redirect('listar_pagos')
        return render(request, 'pago/registrar.html', {
            'form': form,
            'modo': 'crear'
        })

class editar_pago(View):
    def get(self, request, id):
        pago = get_object_or_404(Pago, id=id)
        form = PagoForm(instance=pago)

        qr_url = pago.codigo_qr.imagen_qr.url if pago.codigo_qr else None
        banco_nombre = pago.codigo_qr.banco if pago.codigo_qr else None

        return render(request, 'pago/registrar.html', {
            'form': form,
            'pago': pago,
            'modo': 'editar',
            'qr_url': qr_url,
            'banco_nombre': banco_nombre,
        })

    def post(self, request, id):
        pago = get_object_or_404(Pago, id=id)
        form = PagoForm(request.POST, instance=pago)

        qr_url = pago.codigo_qr.imagen_qr.url if pago.codigo_qr else None
        banco_nombre = pago.codigo_qr.banco if pago.codigo_qr else None

        if form.is_valid():
            form.save()
            messages.success(request, 'Pago actualizado correctamente')
            return redirect('listar_pagos')

        return render(request, 'pago/registrar.html', {
            'form': form,
            'pago': pago,
            'modo': 'editar',
            'qr_url': qr_url,
            'banco_nombre': banco_nombre,
        })

class detalle_pago(View):
    def get(self, request, id):
        pago = get_object_or_404(Pago, id=id)

        qr_url = pago.codigo_qr.imagen_qr.url if pago.codigo_qr else None
        banco_nombre = pago.codigo_qr.banco if pago.codigo_qr else None

        return render(request, 'pago/registrar.html', {
            'pago': pago,
            'modo': 'detalle',
            'qr_url': qr_url,
            'banco_nombre': banco_nombre,
        })

class eliminar_pago(View):
    def get(self, request, id):
        pago = get_object_or_404(Pago, id=id)

        qr_url = pago.codigo_qr.imagen_qr.url if pago.codigo_qr else None
        banco_nombre = pago.codigo_qr.banco if pago.codigo_qr else None

        return render(request, 'pago/registrar.html', {
            'pago': pago,
            'modo': 'eliminar',
            'qr_url': qr_url,
            'banco_nombre': banco_nombre,
        })

    def post(self, request, id):
        pago = get_object_or_404(Pago, id=id)
        pago.delete()
        messages.success(request, 'Pago eliminado correctamente')
        return redirect('listar_pagos')
    
class registrar_pago(View):
    def get(self, request):
        form = PagoForm()
        codigos_qr = CodigoQR.objects.filter(banco__in=['Loja', 'Pichincha'])  # Filtrar los bancos deseados
        return render(request, 'pago/registrar.html', {
            'form': form,
            'modo': 'crear',
            'codigos_qr': codigos_qr
        })

    def post(self, request):
        form = PagoForm(request.POST)
        codigos_qr = CodigoQR.objects.filter(banco__in=['Loja', 'Pichincha'])
        if form.is_valid():
            form.save()
            messages.success(request, 'Pago registrado correctamente')
            return redirect('listar_pagos')
        return render(request, 'pago/registrar.html', {
            'form': form,
            'modo': 'crear',
            'codigos_qr': codigos_qr
        })

    
    
