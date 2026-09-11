"""Senales de la aplicacion.

Avance automatico del cuadro de eliminatoria: en cuanto se cierra el ultimo
partido de una ronda se crea la siguiente. Va en una senal y no dentro de
las vistas del arbitro porque un partido se finaliza desde dos sitios
distintos (el acta y el registro rapido de resultado) y tambien desde el
admin de Django; enganchado al guardado, cualquiera de esas vias dispara el
avance.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Partido

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Partido)
def avanzar_cuadro_al_finalizar(sender, instance, **kwargs):
    # Solo interesa cuando un partido queda cerrado. Los partidos que crea
    # el propio avance nacen en PROGRAMADO, asi que no se realimenta.
    if instance.estado != "FINALIZADO":
        return

    campeonato = instance.campeonato
    if campeonato.tipo_campeonato != "ELIMINATORIA":
        return

    # La importacion va aqui dentro para no crear un ciclo: el modulo de
    # eliminatoria necesita los modelos.
    from core.utils.eliminatoria import avanzar_eliminatoria

    try:
        resultado = avanzar_eliminatoria(campeonato)
    except Exception:
        # Guardar el acta no debe fallar porque el cuadro no pueda avanzar.
        # Queda el boton manual del calendario para reintentarlo.
        logger.exception(
            "No se pudo avanzar el cuadro del campeonato %s", campeonato.pk)
        return

    if resultado.creados:
        logger.info("Eliminatoria %s: creados %s partidos de la ronda siguiente",
                    campeonato.pk, resultado.creados)
