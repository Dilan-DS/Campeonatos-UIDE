from core.models import Campeonato, Equipo, Partido
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

from core.utils.calendario import (
    dias_permitidos_de, horario_y_cancha, primera_fecha_valida,
)

def generar_fixture_liga(campeonato_id):
    try:
        campeonato = Campeonato.objects.get(id=campeonato_id)
    except Campeonato.DoesNotExist:
        print(f"Campeonato con ID {campeonato_id} no encontrado.")
        return

    # 1. Separar equipos por género
    equipos_masculinos = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True, genero='masculino'))
    equipos_femeninos = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True, genero='femenino'))

    print(f"Generando fixture de LIGA para: {campeonato.nombre}")
    print(f"Días de partido permitidos: {campeonato.dias_partido}")

    # Función interna para generar partidos para un grupo de género
    def generar_partidos_por_genero(equipos, genero):
        creados = 0 # Contador de partidos creados
        if len(equipos) < 2:
            print(f"No hay suficientes equipos de género {genero} para generar un fixture.")
            return creados

        # 2. Manejo de número impar de equipos con BYE
        if len(equipos) % 2 != 0:
            equipos.append(None)  # 'None' representa el BYE

        jornadas = []
        equipos_rotando = list(equipos[1:])
        
        for i in range(len(equipos) - 1):
            jornada_actual = []
            # Emparejar el primer equipo con el último de la lista rotativa
            if equipos[0] and equipos_rotando[-1]:
                jornada_actual.append((equipos[0], equipos_rotando[-1]))
            
            # Emparejar el resto de equipos
            for j in range(len(equipos_rotando) // 2):
                if equipos_rotando[j] and equipos_rotando[-(j + 2)]:
                    jornada_actual.append((equipos_rotando[j], equipos_rotando[-(j + 2)]))
            
            jornadas.append(jornada_actual)
            
            # Rotar la lista de equipos (excepto el primero)
            equipos_rotando.insert(0, equipos_rotando.pop())

        # 3. Asignar fechas y crear partidos
        fecha_partido = campeonato.fecha_inicio
        
        # Si el campeonato no tiene dias marcados se permiten los siete. Sin
        # esto la lista quedaba vacia y el bucle de mas abajo no encontraba
        # nunca una fecha valida.
        dias_permitidos_num = dias_permitidos_de(campeonato)

        jornadas_sin_programar = 0

        for jornada in jornadas:
            fecha_partido = primera_fecha_valida(fecha_partido, dias_permitidos_num)

            if fecha_partido > campeonato.fecha_fin:
                # No caben mas jornadas dentro de la ventana del campeonato.
                # Se cuentan para poder avisar: antes se cortaba en silencio
                # y el campeonato quedaba marcado como generado con una liga
                # incompleta.
                jornadas_sin_programar = len(jornadas) - jornadas.index(jornada)
                print(f"ADVERTENCIA: no caben {jornadas_sin_programar} jornada(s) "
                      f"antes del {campeonato.fecha_fin}. El calendario queda incompleto.")
                break

            # Indice del partido dentro de esta fecha, para repartir canchas
            # y turnos sin que dos coincidan en el mismo sitio a la vez.
            indice_en_la_fecha = 0

            for equipo1, equipo2 in jornada:
                if equipo1 and equipo2:  # Asegurarse de que no es un BYE
                    try:
                        hora_partido, lugar = horario_y_cancha(indice_en_la_fecha)
                        partido = Partido(
                            campeonato=campeonato,
                            equipo_local=equipo1,
                            equipo_visitante=equipo2,
                            fecha=fecha_partido,
                            hora=hora_partido,
                            lugar=lugar,
                            arbitro=None
                        )
                        partido.save()
                        creados += 1
                        indice_en_la_fecha += 1
                        print(f"CREADO: {equipo1.nombre} vs {equipo2.nombre} ({fecha_partido} {hora_partido} {lugar})")
                    except ValidationError as e:
                        print(f"VALIDATION ERROR: {equipo1.nombre} vs {equipo2.nombre} el {fecha_partido}: {e.message_dict}")
                    except Exception as e:
                        print(f"ERROR inesperado: {equipo1.nombre} vs {equipo2.nombre} el {fecha_partido}: {e}")

            fecha_partido += timedelta(days=1)

        if jornadas_sin_programar:
            incompletos.append(genero)
        return creados

    # Generos cuyo calendario no cupo entero en la ventana del campeonato.
    incompletos = []

    total_creados = 0
    total_creados += generar_partidos_por_genero(equipos_masculinos, 'masculino')
    total_creados += generar_partidos_por_genero(equipos_femeninos, 'femenino')

    print(f"Fixture de liga generado para {campeonato.nombre}. Total partidos creados: {total_creados}")
    if incompletos:
        print(f"ATENCION: el calendario quedo incompleto en: {', '.join(incompletos)}")
    return total_creados

