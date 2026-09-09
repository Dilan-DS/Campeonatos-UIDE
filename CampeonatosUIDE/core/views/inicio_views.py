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
# Esta vista renderiza la página de inicio pública del sitio.
def vista_inicio(request):
    from django.utils import timezone
    from django.shortcuts import render
    from django.apps import apps # Added this import

    # Helper function to safely get models
    def _get_model(model_name):
        try:
            return apps.get_model('core', model_name)
        except LookupError:
            return None

    ctx = {}

    # 1) Campeonatos activos (CharField SI/NO)
    Campeonato = _get_model('Campeonato')
    if Campeonato:
        ctx["campeonatos"] = (
            Campeonato.objects.filter(activo="SI").order_by("-fecha_inicio")[:6]
        )
    else:
        ctx["campeonatos"] = []

    # 2) Próximos partidos (si el modelo existe)
    Partido = _get_model('Partido')
    if Partido:
        try:
            ctx["proximos_partidos"] = (
                Partido.objects.filter(
                    campeonato__activo="SI",
                    fecha__gte=timezone.now()
                )
                .select_related(
                    'campeonato',          # siempre
                    'campeonato__deporte', # deporte viene POR campeonato
                    'equipo_local',
                    'equipo_visitante',
                    'arbitro'
                )
                .order_by("fecha")[:6]
            )
        except Exception:
            ctx["proximos_partidos"] = []
    else:
        ctx["proximos_partidos"] = []

    # Helper para filtrar por campos “publicados/visibles” si existen
    def _filtrar_publico(qs, pares):
        for campo, valor in pares:
            try:
                qs.model._meta.get_field(campo)
                qs = qs.filter(**{campo: valor})
            except Exception:
                pass
        return qs

    # 3) Transmisiones (solo publicadas/visibles si esos campos existen)
    Transmision = _get_model('Transmision')
    if Transmision:
        try:
            trans = Transmision.objects.all().order_by("-id")
            trans = _filtrar_publico(trans, [("estado", "PUBLICADO"), ("publicado", True), ("visible", True), ("activo", "SI")])
            ctx["transmisiones"] = trans[:4]
        except Exception:
            ctx["transmisiones"] = []
    else:
        ctx["transmisiones"] = []

    # 4) Galería (si hay modelo de imágenes para público)
    ImagenGaleria = _get_model('ImagenGaleria')
    if ImagenGaleria:
        try:
            gal = ImagenGaleria.objects.all().order_by("-id")
            gal = _filtrar_publico(gal, [("publica", True), ("visible", True), ("estado", "PUBLICADO")])
            ctx["imagenes_galeria"] = gal[:8]
        except Exception:
            ctx["imagenes_galeria"] = []
    else:
        ctx["imagenes_galeria"] = []

    # 5) Noticias (admin publica; el público solo ve publicadas)
    Noticia = _get_model('Noticia')
    if Noticia:
        try:
            news = Noticia.objects.all().order_by("-id")
            news = _filtrar_publico(news, [("publica", True), ("visible", True), ("estado", "PUBLICADO")])
            ctx["noticias"] = news[:5]
        except Exception:
            ctx["noticias"] = []
    else:
        ctx["noticias"] = []

    # 6) Testimonios (igual: solo los publicados/visibles)
    Testimonio = _get_model('Testimonio')
    if Testimonio:
        try:
            tes = Testimonio.objects.all().order_by("-id")
            tes = _filtrar_publico(tes, [("publico", True), ("visible", True), ("estado", "PUBLICADO")])
            ctx["testimonios"] = tes[:5]
        except Exception:
            ctx["testimonios"] = []
    else:
        ctx["testimonios"] = []

    if request.method == 'POST':
        accion = request.POST.get('accion')
        rol = getattr(request.user, 'rol', None)
        is_auth = request.user.is_authenticated
        try:
            # ---------- TESTIMONIO: lo puede enviar cualquiera (incluye anónimo) ----------
            if accion == 'enviar_testimonio':
                from core.models import Testimonio  # ajusta si el nombre difiere
                texto = (request.POST.get('texto') or "").strip()
                autor = (request.POST.get('autor') or "").strip()
                if not texto:
                    messages.error(request, "Escribe tu testimonio.")
                    return redirect('vista_inicio')
                obj = Testimonio()
                if hasattr(obj, 'texto'):
                    obj.texto = texto
                elif hasattr(obj, 'contenido'):
                    obj.contenido = texto
                if hasattr(obj, 'autor_nombre'):
                    obj.autor_nombre = autor or "Anónimo"
                if hasattr(obj, 'usuario') and is_auth:
                    obj.usuario = request.user
                if hasattr(obj, 'publicado'):
                    obj.publicado = False
                if hasattr(obj, 'estado'):
                    obj.estado = 'PENDIENTE'
                obj.save()
                messages.success(request, "¡Gracias! Tu testimonio quedó enviado para revisión.")
                return redirect('vista_inicio')
            # ---------- NOTICIA: SOLO ADMIN ----------
            if accion == 'enviar_noticia':
                if rol != 'ADMIN':
                    messages.error(request, "Solo el administrador puede publicar noticias.")
                    return redirect('vista_inicio')
                from core.models import Noticia  # ajusta si el nombre difiere
                titulo = (request.POST.get('titulo') or "").strip()
                cuerpo = (request.POST.get('cuerpo') or "").strip()
                if not titulo or not cuerpo:
                    messages.error(request, "Completa título y contenido.")
                    return redirect('vista_inicio')
                obj = Noticia()
                if hasattr(obj, 'titulo'):
                    obj.titulo = titulo
                if hasattr(obj, 'contenido'):
                    obj.contenido = cuerpo
                if hasattr(obj, 'publicado'):
                    obj.publicado = True  # o False si requiere aprobación
                if hasattr(obj, 'estado') and not hasattr(obj, 'publicado'):
                    obj.estado = 'PUBLICADO'
                obj.save()
                messages.success(request, "Noticia publicada.")
                return redirect('vista_inicio')
            # ---------- GALERÍA: SOLO JUGADOR ----------
            if accion == 'enviar_imagen':
                if rol != 'JUGADOR':
                    messages.error(request, "Solo los jugadores pueden subir imágenes a la galería.")
                    return redirect('vista_inicio')
                imagen = request.FILES.get('imagen')
                descripcion = (request.POST.get('descripcion') or "").strip()
                if not imagen:
                    messages.error(request, "Selecciona una imagen.")
                    return redirect('vista_inicio')
                # Ajusta el modelo real de galería
                try:
                    from core.models import ImagenGaleria as Galeria
                except Exception:
                    from core.models import Galeria
                obj = Galeria()
                if hasattr(obj, 'imagen'):
                    obj.imagen = imagen
                elif hasattr(obj, 'archivo'):
                    obj.archivo = imagen
                if hasattr(obj, 'descripcion'):
                    obj.descripcion = descripcion
                if hasattr(obj, 'publicado'):
                    obj.publicado = False
                if hasattr(obj, 'estado'):
                    obj.estado = 'PENDIENTE'
                if hasattr(obj, 'usuario') and is_auth:
                    obj.usuario = request.user
                obj.save()
                messages.success(request, "Imagen enviada. Queda pendiente de aprobación.")
                return redirect('vista_inicio')
        except Exception as e:
            messages.error(request, f"Ocurrió un error al enviar: {e}")
            return redirect('vista_inicio')
    return render(request, 'publica/inicio_publico.html', ctx)

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