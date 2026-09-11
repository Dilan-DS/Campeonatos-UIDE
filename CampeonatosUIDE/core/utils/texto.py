"""Normalizacion de texto compartida.

`sin_acentos` existe porque el codigo compara el nombre de un deporte
contra literales sin tilde ("FUTBOL", "FUTBOL" mayusculas) en varios
sitios (equipo_views, jugador_views, Equipo.puntos_totales), pero nada
impide que el Deporte se haya guardado como "Fútbol" -- la forma natural
en español, y la que usa el propio formulario de alta de deportes. Sin
esta normalizacion esa comparacion nunca coincide y las estadisticas de
futbol (goles por jugador, puntos por partido) quedan siempre en cero.
"""
import unicodedata


def sin_acentos(texto):
    if not texto:
        return texto
    descompuesto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c))
