from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import CodigoQR
from .forms import CodigoQRForm

def listar_codigos_qr(request):
    query = request.GET.get("q", "")
    if query:
        codigos_qr = CodigoQR.objects.filter(
            Q(banco__icontains=query) | Q(descripcion__icontains=query)
        )
    else:
        codigos_qr = CodigoQR.objects.all()

    return render(request, 'codigoqr/listar.html', {
        'codigos_qr': codigos_qr
    })

# ✅ Registrar un nuevo código QR
def registrar_codigo_qr(request):
    if request.method == 'POST':
        form = CodigoQRForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Código QR registrado con éxito.")
            return redirect('listar_codigos_qr')
    else:
        form = CodigoQRForm()
    return render(request, 'codigoqr/registrar.html', {'form': form})

# ✅ Editar código QR
def editar_codigo_qr(request, pk):
    codigo = get_object_or_404(CodigoQR, pk=pk)
    if request.method == 'POST':
        form = CodigoQRForm(request.POST, request.FILES, instance=codigo)
        if form.is_valid():
            form.save()
            messages.success(request, "Código QR actualizado con éxito.")
            return redirect('listar_codigos_qr')
    else:
        form = CodigoQRForm(instance=codigo)
    return render(request, 'codigoqr/editar.html', {'form': form, 'codigo': codigo})

# ✅ Eliminar código QR
def eliminar_codigo_qr(request, pk):
    codigo = get_object_or_404(CodigoQR, pk=pk)
    if request.method == 'POST':
        codigo.delete()
        messages.success(request, "Código QR eliminado correctamente.")
        return redirect('listar_codigos_qr')
    return render(request, 'codigoqr/eliminar.html', {'codigo': codigo})
