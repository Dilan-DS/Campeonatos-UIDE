"""Avance de un cuadro de eliminatoria.

generar_fixture_eliminatoria solo crea la primera ronda: con 8 equipos
programa los 4 cruces y ahi se queda, cuando un cuadro completo necesita 7
partidos (4 + 2 semifinales + 1 final). Este modulo se encarga del resto,
cruzando a los ganadores cuando la ronda termina.

Se usa desde dos sitios, y los dos llaman a `avanzar_eliminatoria`:

  · automaticamente, desde la senal que escucha el guardado de un partido
    (core/signals.py), en cuanto se cierra el ultimo partido de la ronda;
  · a mano, con el boton "Avanzar ronda" del calendario, por si el avance
    automatico no se hubiera disparado.

Como el calculo parte siempre del estado de la base de datos y no de quien
llama, las dos vias dan el mismo resultado y ejecutarlas dos veces no crea
partidos de mas.
"""
from datetime import timedelta

from core.utils.calendario import (
    dias_permitidos_de, horario_y_cancha, primera_fecha_valida,
)


class ResultadoDelAvance:
    """Que paso al intentar avanzar, para poder explicarselo al usuario."""

    def __init__(self):
        self.creados = 0
        self.campeones = []        # (genero, equipo) ya sin rival posible
        self.en_curso = []         # generos con partidos aun sin jugar
        self.empates = []          # (genero, partido) sin ganador
        self.sin_cuadro = []       # generos sin eliminatoria empezada

    @property
    def hay_algo_que_contar(self):
        return bool(self.creados or self.campeones or self.empates
                    or self.en_curso or self.sin_cuadro)


def _ganador(partido):
    """Equipo que pasa de ronda, o None si aun no hay quien pase.

    En el tiempo reglamentario manda el marcador. Si acaba empatado decide
    la tanda de penaltis, que el arbitro anota en el acta. Un empate sin
    tanda no da ganador a proposito: el cuadro se queda parado hasta que el
    arbitro la registre.
    """
    if partido.resultado_local is None or partido.resultado_visitante is None:
        return None
    if partido.resultado_local > partido.resultado_visitante:
        return partido.equipo_local
    if partido.resultado_visitante > partido.resultado_local:
        return partido.equipo_visitante
    return partido.ganador_por_penales()


def _siguiente_fecha(campeonato, desde):
    """Primer dia permitido a partir del dia siguiente al indicado."""
    dias = dias_permitidos_de(campeonato)
    return primera_fecha_valida(desde + timedelta(days=1), dias)


def _avanzar_genero(campeonato, genero, resultado):
    from core.models import Equipo, Partido

    partidos = list(
        Partido.objects.filter(campeonato=campeonato,
                               equipo_local__genero=genero)
        .select_related("equipo_local", "equipo_visitante")
        .order_by("ronda", "fecha", "hora", "id")
    )
    if not partidos:
        resultado.sin_cuadro.append(genero)
        return

    ultima_ronda = max(p.ronda or 1 for p in partidos)
    de_la_ronda = [p for p in partidos if (p.ronda or 1) == ultima_ronda]

    # Mientras quede algun partido por cerrar no se puede cruzar nada.
    if any(p.estado != "FINALIZADO" for p in de_la_ronda):
        resultado.en_curso.append(genero)
        return

    ganadores = []
    for partido in de_la_ronda:
        vencedor = _ganador(partido)
        if vencedor is None:
            # Empate sin tanda de penaltis que lo resuelva: la ronda se
            # queda parada hasta que el arbitro anote la tanda en el acta.
            resultado.empates.append((genero, partido))
            return
        ganadores.append(vencedor)

    # Equipos que siguen vivos sin haber jugado esta ronda: son los que
    # descansaron (BYE) en el sorteo inicial. No se guardan en ningun sitio,
    # se deducen de quien no ha jugado todavia.
    han_jugado = {p.equipo_local_id for p in partidos} | {p.equipo_visitante_id for p in partidos}
    descansan = list(
        Equipo.objects.filter(campeonato=campeonato, aprobado=True, genero=genero)
        .exclude(id__in=han_jugado).order_by("id")
    )

    clasificados = ganadores + descansan

    if len(clasificados) == 1:
        resultado.campeones.append((genero, clasificados[0]))
        return
    if len(clasificados) == 0:
        return

    # Se cruzan de dos en dos respetando el orden del cuadro: el ganador del
    # primer partido contra el del segundo, y asi sucesivamente.
    fecha = _siguiente_fecha(campeonato, max(p.fecha for p in de_la_ronda))
    indice_en_la_fecha = 0

    for i in range(0, len(clasificados) - 1, 2):
        local, visitante = clasificados[i], clasificados[i + 1]
        hora, lugar = horario_y_cancha(indice_en_la_fecha)
        Partido.objects.create(
            campeonato=campeonato,
            equipo_local=local,
            equipo_visitante=visitante,
            fecha=fecha,
            hora=hora,
            lugar=lugar,
            estado="PROGRAMADO",
            ronda=ultima_ronda + 1,
            arbitro=None,
        )
        resultado.creados += 1
        indice_en_la_fecha += 1

    # Si queda uno suelto no se le crea partido: descansa y entrara en la
    # ronda siguiente, igual que los BYE del sorteo inicial.


def avanzar_eliminatoria(campeonato):
    """Crea la siguiente ronda de cada genero cuando la actual ha terminado.

    No hace nada si el campeonato no es de eliminatoria, si la ronda sigue
    en juego o si hay algun empate sin resolver.
    """
    resultado = ResultadoDelAvance()
    if campeonato.tipo_campeonato != "ELIMINATORIA":
        return resultado

    for genero in ("masculino", "femenino"):
        _avanzar_genero(campeonato, genero, resultado)

    return resultado
