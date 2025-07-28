from django.shortcuts import render
from core.models import Campeonato, Partido, Transmision, ImagenGaleria, Noticia, Testimonio
from django.utils import timezone

def inicio_publico(request):
    campeonatos = Campeonato.objects.filter(fecha_fin__gte=timezone.now())
    proximos_partidos = Partido.objects.filter(fecha__gte=timezone.now()).order_by('fecha')[:5]
    transmisiones = Transmision.objects.all()[:3]
    imagenes_galeria = ImagenGaleria.objects.all()[:6]
    noticias = Noticia.objects.order_by('-fecha_publicacion')[:5]
    testimonios = Testimonio.objects.order_by('-fecha')[:3]
    return render(request, 'publico/inicio_publico.html', {
        'campeonatos': campeonatos,
        'proximos_partidos': proximos_partidos,
        'transmisiones': transmisiones,
        'imagenes_galeria': imagenes_galeria,
        'noticias': noticias,
        'testimonios': testimonios,
    })

# Esta vista renderiza la página de inicio pública del sitio.
def vista_inicio_publico(request):
    # Si el usuario ya está autenticado, redirige al dashboard correspondiente
    return render(request, 'publica/inicio_publico.html')
# Esta vista renderiza la página de inicio pública del sitio.
def vista_inicio(request):
    # Si el usuario ya está autenticado, redirige al dashboard correspondiente
    return render(request, 'publica/inicio_publico.html')