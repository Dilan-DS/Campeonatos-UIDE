"""Piezas comunes a los generadores de calendario.

Los tres generadores repetian el mismo mapa de dias de la semana. Dos de
ellos (liga y eliminatoria) lo usaban sin red: si el campeonato no tenia
ningun dia marcado —y el campo lo permite, es blank=True con default=[]—
la lista de dias permitidos quedaba vacia y este bucle no encontraba
nunca una fecha valida:

    while fecha.weekday() not in dias_permitidos:
        fecha += timedelta(days=1)

No se colgaba para siempre: avanzaba la fecha unos 2,9 millones de veces
hasta pasar del ano 9999 y reventaba con OverflowError, que desde la web
salia como un error 500.
"""
from datetime import date, datetime, time, timedelta


DIAS_DE_LA_SEMANA = {
    "LUNES": 0, "MARTES": 1, "MIERCOLES": 2, "JUEVES": 3,
    "VIERNES": 4, "SABADO": 5, "DOMINGO": 6,
}

# Reparto de partidos dentro de una misma fecha.
HORA_DE_INICIO = time(18, 0)
CANCHAS_DISPONIBLES = 5
MINUTOS_POR_PARTIDO = 90

# Base arbitraria para poder sumar minutos a una hora. Solo se usa la parte
# horaria del resultado.
_DIA_DE_REFERENCIA = date(2000, 1, 1)


def dias_permitidos_de(campeonato):
    """Dias de la semana en los que se puede jugar, como numeros 0-6.

    Si el campeonato no tiene dias marcados, o trae un valor que no esta en
    el mapa, se permiten los siete. Es lo que ya hacia el generador de fase
    de grupos, y es preferible a programar en una fecha imposible o a dejar
    el campeonato sin calendario.
    """
    configurados = getattr(campeonato, "dias_partido", None) or []
    if not configurados:
        return list(range(7))
    try:
        return [DIAS_DE_LA_SEMANA[str(dia).upper()] for dia in configurados]
    except KeyError:
        return list(range(7))


def primera_fecha_valida(desde, dias_permitidos):
    """Avanza hasta el primer dia permitido, sin salirse del calendario.

    dias_permitidos nunca deberia llegar vacio porque dias_permitidos_de ya
    devuelve los siete dias en ese caso, pero se comprueba igualmente: es
    justo la condicion que provocaba el OverflowError.
    """
    if not dias_permitidos:
        dias_permitidos = list(range(7))
    fecha = desde
    # Como mucho hay que avanzar seis dias para encontrar uno de los
    # permitidos, asi que el bucle tiene un tope natural.
    for _ in range(7):
        if fecha.weekday() in dias_permitidos:
            return fecha
        fecha += timedelta(days=1)
    return desde


def horario_y_cancha(indice_en_la_fecha):
    """Reparte los partidos de un mismo dia en canchas y horas distintas.

    Antes todos los partidos de una jornada se creaban a las 18:00 con
    `Cancha {random.randint(1, 5)}`, de modo que dos partidos podian caer a
    la misma hora en la misma cancha. Ahora se ocupan primero las cinco
    canchas a la hora de inicio y, si hay mas partidos ese dia, se pasa al
    siguiente turno.
    """
    cancha = indice_en_la_fecha % CANCHAS_DISPONIBLES + 1
    turno = indice_en_la_fecha // CANCHAS_DISPONIBLES
    inicio = datetime.combine(_DIA_DE_REFERENCIA, HORA_DE_INICIO)
    hora = (inicio + timedelta(minutes=MINUTOS_POR_PARTIDO * turno)).time()
    return hora, f"Cancha {cancha}"
