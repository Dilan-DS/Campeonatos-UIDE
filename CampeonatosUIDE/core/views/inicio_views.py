from django.shortcuts import render
from core.models import Campeonato, Partido, Transmision, ImagenGaleria, Noticia, Testimonio
from django.utils import timezone


def _contexto_portada():
    """Datos que muestra la portada pública (publica/inicio_publico.html).

    La plantilla espera campeonatos, proximos_partidos, transmisiones,
    imagenes_galeria, noticias y testimonios. Antes vista_inicio_publico
    renderizaba sin contexto, así que la portada mostraba siempre sus
    estados vacíos ("No hay campeonatos activos.") aunque hubiera datos.
    """
    hoy = timezone.localdate()
    return {
        'campeonatos': (
            Campeonato.objects
            .filter(activo='SI', es_publico='SI')
            .select_related('deporte')
            .order_by('-fecha_inicio')[:6]
        ),
        'proximos_partidos': (
            Partido.objects
            .filter(campeonato__activo='SI', campeonato__es_publico='SI', fecha__gte=hoy)
            .select_related('campeonato', 'campeonato__deporte',
                            'equipo_local', 'equipo_visitante')
            .order_by('fecha', 'hora')[:6]
        ),
        'transmisiones': (
            Transmision.objects
            .filter(activa=True)
            .select_related('campeonato', 'partido')
            .order_by('-id')[:4]
        ),
        'imagenes_galeria': ImagenGaleria.objects.order_by('-creado_en')[:8],
        'noticias': Noticia.objects.order_by('-creado_en')[:5],
        'testimonios': Testimonio.objects.order_by('-creado_en')[:5],
    }


# Esta vista renderiza la página de inicio pública del sitio.
def vista_inicio_publico(request):
    return render(request, 'publica/inicio_publico.html', _contexto_portada())


def vista_inicio(request):
    """Portada para usuarios autenticados (ruta /dashboard/).

    Renderiza la misma plantilla que la portada publica, asi que reutiliza
    _contexto_portada en lugar de repetir las consultas.

    Antes construia su propio contexto con apps.get_model y hasattr sobre
    campos que no existen en los modelos ("publicado", "visible",
    "estado"), y sobre todo no filtraba es_publico, asi que esta ruta
    seguia mostrando campeonatos no publicos. Tambien llevaba un bloque
    POST para enviar testimonios, noticias e imagenes que ninguna
    plantilla enviaba y que ademas usaba messages y redirect sin
    importarlos: se habria caido con NameError en la primera linea.
    """
    return render(request, 'publica/inicio_publico.html', _contexto_portada())

def equipo_publico(request):
    miembros = [
        {
            "nombre": "Felix Melgar Rodas",
            "rol": "Desarrollador",
            "telefono": "",
            "correo": "",
            "foto": "img/integrante1.png",
        },
        {
            "nombre": "Stephano Dilan Galvez Perez",
            "rol": "Desarrollador",
            "telefono": "+593 99 070 6018",
            "correo": "stgalvezpe@uide.edu.ec",
            "foto": "img/integrante2.png",
        },
        {
            "nombre": "Jhosty Sot",
            "rol": "Desarrollador",
            "telefono": "",
            "correo": "",
            "foto": "img/integrante3.png", 
        },
    ]
    return render(request, "publica/equipo.html", {"miembros": miembros})

def resultados_publicos(request):
    # El directorio de plantillas es 'publica/', no 'publico/': con la ruta
    # anterior /resultados-publicos/ respondía TemplateDoesNotExist.
    partidos_finalizados = (
        Partido.objects
        .filter(estado='FINALIZADO')
        .select_related('campeonato', 'campeonato__deporte',
                        'equipo_local', 'equipo_visitante')
        .order_by('-fecha', '-hora')
    )
    return render(request, 'publica/resultados_publicos.html',
                  {'partidos_finalizados': partidos_finalizados})