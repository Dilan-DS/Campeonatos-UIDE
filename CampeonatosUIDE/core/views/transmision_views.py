from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Transmision, Campeonato


# ========================
# TRANSMISIONES
# ========================

def es_admin(user):
    return user.rol == 'ADMIN'


def listar_transmisiones(request):
    # Obtiene todas las transmisiones registradas en la base de datos
    transmisiones = Transmision.objects.all()
    # Ordena las transmisiones por campeonato y nombre
    return render(request, 'transmision/listar_transmisiones.html', {'transmisiones': transmisiones})

def registrar_transmision(request):
    # Verifica si la solicitud es POST (envío de formulario)
    if request.method == 'POST':
        # Obtiene los datos del formulario
        nombre = request.POST.get('nombre')
        # Obtiene la URL de la transmisión
        url = request.POST.get('url')
        # Obtiene el ID del campeonato desde la solicitud POST
        campeonato_id = request.POST.get('campeonato')
        # Verifica si todos los campos son obligatorios
        campeonato = get_object_or_404(Campeonato, id=campeonato_id)
        # Si todos los campos son válidos, crea una nueva transmisión
        Transmision.objects.create(nombre=nombre, url=url, campeonato=campeonato)
        # Muestra un mensaje de éxito al usuario
        return redirect('listar_transmisiones')
    campeonatos = Campeonato.objects.all()
    return render(request, 'transmision/registrar_transmision.html', {'campeonatos': campeonatos})

def detalle_transmision(request, id):
    # Obtiene la transmisión por su ID, o devuelve un error 404 si no se encuentra
    transmision = get_object_or_404(Transmision, id=id)
    # Renderiza la plantilla 'detalle_transmision.html' con la transmisión
    return render(request, 'transmision/detalle_transmision.html', {'transmision': transmision})

# Editar una transmisión (solo admin)
@login_required
@user_passes_test(es_admin)
def editar_transmision(request, id):
    # Obtiene la transmisión por su ID, o devuelve un error 404 si no se encuentra
    transmision = get_object_or_404(Transmision, id=id)

    if request.method == 'POST':
        # Si la solicitud es POST, obtiene los datos del formulario
        nombre = request.POST.get('nombre')
        # Obtiene la URL de la transmisión
        url = request.POST.get('url')
        # Obtiene el ID del campeonato desde la solicitud POST
        campeonato_id = request.POST.get('campeonato')

        if nombre and url and campeonato_id:
            # Verifica si todos los campos son obligatorios
            transmision.nombre = nombre
            # Actualiza la URL de la transmisión
            transmision.url = url
            # Obtiene el campeonato correspondiente al ID proporcionado
            transmision.campeonato = get_object_or_404(Campeonato, id=campeonato_id)
            # Guarda los cambios en la transmisión
            transmision.save()
            # Muestra un mensaje de éxito al usuario
            messages.success(request, 'Transmisión actualizada correctamente.')
            # Redirige al usuario a la lista de transmisiones
            return redirect('listar_transmisiones')
        else:
            # Si algún campo está vacío, muestra un mensaje de error
            messages.error(request, 'Todos los campos son obligatorios.')

    campeonatos = Campeonato.objects.all()
    # Si la solicitud no es POST, crea un formulario con los datos de la transmisión existente
    return render(request, 'transmision/editar_transmision.html', {
        
        'transmision': transmision,
        'campeonatos': campeonatos
    })
# Eliminar una transmisión (solo admin)
@login_required
@user_passes_test(es_admin)
# función para eliminar una transmisión
def eliminar_transmision(request, id):  
    # Obtiene la transmisión por su ID, o devuelve un error 404 si no se encuentra
    transmision = get_object_or_404(Transmision, id=id)

    # Verifica si la solicitud es POST (confirmación de eliminación)
    if request.method == 'POST':
        # Si la solicitud es POST, elimina la transmisión de la base de datos
        transmision.delete()
        # Muestra un mensaje de éxito al usuario
        messages.success(request, 'Transmisión eliminada correctamente.')
        # Redirige al usuario a la lista de transmisiones
        return redirect('listar_transmisiones')

    return render(request, 'transmision/eliminar_transmision.html', {
        # Renderiza la plantilla de confirmación de eliminación con la transmisión
        'transmision': transmision
    })
