"""Cálculo compartido de la tabla de posiciones basada en partidos finalizados."""

from collections import defaultdict

from core.models import Equipo, Partido


def calcular_tabla_posiciones(campeonato):
    """Devuelve las mismas columnas de tabla usando dos consultas acotadas.

    La lógica de puntaje conserva la implementación existente: tres puntos por
    victoria y uno por empate. Solo se consideran equipos aprobados y partidos
    FINALIZADO del campeonato indicado.
    """
    equipos = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True))
    acumulados = defaultdict(lambda: {
        "pj": 0, "pg": 0, "pe": 0, "pp": 0, "gf": 0, "gc": 0, "puntos": 0,
    })

    partidos = Partido.objects.filter(
        campeonato=campeonato,
        estado="FINALIZADO",
    ).values_list(
        "equipo_local_id",
        "equipo_visitante_id",
        "resultado_local",
        "resultado_visitante",
    )

    for local_id, visitante_id, resultado_local, resultado_visitante in partidos:
        # Los resultados son opcionales en el modelo; evitar cambiar el
        # comportamiento de la vista ante un partido finalizado incompleto.
        if resultado_local is None or resultado_visitante is None:
            continue

        local = acumulados[local_id]
        visitante = acumulados[visitante_id]
        local["pj"] += 1
        visitante["pj"] += 1
        local["gf"] += resultado_local
        local["gc"] += resultado_visitante
        visitante["gf"] += resultado_visitante
        visitante["gc"] += resultado_local

        if resultado_local > resultado_visitante:
            local["pg"] += 1
            visitante["pp"] += 1
            local["puntos"] += 3
        elif resultado_local < resultado_visitante:
            visitante["pg"] += 1
            local["pp"] += 1
            visitante["puntos"] += 3
        else:
            local["pe"] += 1
            visitante["pe"] += 1
            local["puntos"] += 1
            visitante["puntos"] += 1

    tabla = []
    for equipo in equipos:
        fila = acumulados[equipo.id]
        tabla.append({
            "equipo": equipo,
            **fila,
            "gd": fila["gf"] - fila["gc"],
        })

    return sorted(tabla, key=lambda fila: (fila["puntos"], fila["gd"], fila["gf"]), reverse=True)
