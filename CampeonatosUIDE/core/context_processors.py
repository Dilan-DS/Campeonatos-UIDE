from .models import Campeonato

def menu_context(request):
    campeonato_activo = Campeonato.objects.filter(activo='SI', fixture_generado=True).first()
    return {
        'campeonato_listo_para_ver': campeonato_activo
    }