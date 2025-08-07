from .generar_fixture_fase_grupos import generar_fixture_fase_grupos
from .generar_fixture_eliminatoria import generar_fixture_eliminatoria
from .generar_fixture_liga import generar_fixture_liga

def generar_fixture_campeonato(campeonato_id, tipo_campeonato):
    if tipo_campeonato == 'FASE_GRUPOS':
        generar_fixture_fase_grupos(campeonato_id)
    elif tipo_campeonato == 'ELIMINATORIA':
        generar_fixture_eliminatoria(campeonato_id)
    elif tipo_campeonato == 'LIGA':
        generar_fixture_liga(campeonato_id)
    else:
        print(f"Tipo de campeonato desconocido: {tipo_campeonato}")
