# core/utils/generar_fixture_fase_grupos.py

from core.models import Campeonato, Equipo, Partido, Arbitro
from datetime import timedelta, time, date, datetime
import random
import itertools
from django.core.exceptions import ValidationError


def generar_fixture_fase_grupos(campeonato_id):
    """Genera fixture de fase de grupos para un campeonato.
    Siempre retorna int (cantidad de partidos creados).
    """
    # 1) Obtener campeonato
    try:
        campeonato = Campeonato.objects.get(id=campeonato_id)
    except Campeonato.DoesNotExist:
        print(f"Campeonato con ID {campeonato_id} no encontrado.")
        return 0  # <-- siempre entero

    print(f"Generando fixture de FASE DE GRUPOS para: {campeonato.nombre}")

    # 2) Equipos aprobados por género
    equipos_m = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True, genero="masculino"))
    equipos_f = list(Equipo.objects.filter(campeonato=campeonato, aprobado=True, genero="femenino"))

    # 3) Helper por género (SIEMPRE devuelve int)
    def generar_partidos_por_genero(equipos, genero):
        creados = 0 # Contador de partidos creados
        # Calcular num_grupos dinámicamente
        num_grupos_original = 4 # Valor por defecto si no se especifica
        num_grupos_actual = max(1, min(num_grupos_original, len(equipos) // 2)) # Al menos 1 grupo si hay equipos
        
        if len(equipos) < 2: # Necesitamos al menos 2 equipos para un partido
            print(f"No hay suficientes equipos de género {genero} para generar enfrentamientos.")
            return creados # Return 0 if not enough teams

        random.shuffle(equipos)

        # 2. Distribuir equipos en grupos
        grupos = [[] for _ in range(num_grupos_actual)]
        for i, equipo in enumerate(equipos):
            grupos[i % num_grupos_actual].append(equipo)

        # normalizar fechas
        fecha_inicio = getattr(campeonato, "fecha_inicio", None)
        if isinstance(fecha_inicio, datetime):
            fecha_inicio = fecha_inicio.date()
        if fecha_inicio is None:
            # fallback seguro: hoy
            fecha_inicio = date.today()

        fecha_fin = getattr(campeonato, "fecha_fin", None)
        if isinstance(fecha_fin, datetime):
            fecha_fin = fecha_fin.date()
        if fecha_fin is not None and not isinstance(fecha_fin, date):
            fecha_fin = None  # si viene raro, ignóralo

        # días permitidos
        DIAS_MAP = {"LUNES": 0, "MARTES": 1, "MIERCOLES": 2, "JUEVES": 3, "VIERNES": 4, "SABADO": 5, "DOMINGO": 6}
        dias_cfg = getattr(campeonato, "dias_partido", None) or []
        try:
            dias_permitidos = [DIAS_MAP[d.upper()] for d in dias_cfg] if dias_cfg else list(range(7))
        except Exception:
            dias_permitidos = list(range(7))  # si algo viene mal, permitir todos

        # por cada grupo, generamos todos contra todos
        for idx_grupo, grupo in enumerate(grupos, start=1):
            print(f"--- Generando partidos para el Grupo {idx_grupo} ({genero}) ---")
            if len(grupo) < 2:
                continue

            # BYE si impar
            if len(grupo) % 2 != 0:
                grupo.append(None)

            # Emparejar equipos para la primera ronda (0 vs 1, 2 vs 3, etc.)
            # Mezclar el grupo para emparejamientos aleatorios en la primera ronda
            random.shuffle(grupo)
            
            # Generar emparejamientos de la primera ronda
            enfrentamientos_primera_ronda = []
            for k in range(0, len(grupo), 2):
                if k + 1 < len(grupo):
                    equipo1, equipo2 = grupo[k], grupo[k+1]
                    if equipo1 and equipo2: # Asegurarse de que no es un BYE
                        enfrentamientos_primera_ronda.append((equipo1, equipo2))

            # fecha base por grupo (así no “consume” todo un grupo la línea de tiempo)
            fecha_partido = fecha_inicio

            for eq1, eq2 in enfrentamientos_primera_ronda:
                if not eq1 or not eq2:  # BYE (should be handled by the above logic, but as a safeguard)
                    continue

                # mover a un día permitido
                while fecha_partido.weekday() not in dias_permitidos:
                    fecha_partido += timedelta(days=1)

                # respetar fecha_fin si existe: si nos pasamos, reinicia desde inicio para no quedar en 0
                if fecha_fin and fecha_partido > fecha_fin:
                    print("ADVERTENCIA: Se ha superado la fecha de fin; reiniciando calendario desde fecha_inicio.")
                    fecha_partido = fecha_inicio
                    while fecha_partido.weekday() not in dias_permitidos:
                        fecha_partido += timedelta(days=1)

                # árbitro opcional
                arbitro = next(arbitro_cycle) if arbitro_cycle else None

                # datos mínimos
                hora_partido = time(18, 0)
                lugar = f"Cancha Grupo {idx_grupo}"

                try:
                    partido = Partido(
                        campeonato=campeonato,
                        equipo_local=eq1,
                        equipo_visitante=eq2,
                        fecha=fecha_partido,   # DateField
                        hora=hora_partido,     # TimeField
                        lugar=lugar,
                        arbitro=arbitro,
                        estado="PROGRAMADO",   # ajusta al choice de tu modelo
                    )
                    partido.full_clean()
                    partido.save()
                    creados += 1
                    print(f"CREADO: {eq1.nombre} vs {eq2.nombre} ({fecha_partido} {hora_partido})")
                except ValidationError as e:
                    print(f"VALIDATION ERROR: {eq1 and eq1.nombre} vs {eq2 and eq2.nombre} "
                          f"el {fecha_partido}: {e.message_dict}")
                except Exception as e:
                    print(f"ERROR inesperado: {eq1 and eq1.nombre} vs {eq2 and eq2.nombre} "
                          f"el {fecha_partido}: {e}")

                # siguiente fecha
                fecha_partido += timedelta(days=1)

        return creados  # SIEMPRE int

    # 4) Ejecutar por género (a prueba de None)
    total_creados = 0
    total_creados += (generar_partidos_por_genero(equipos_m, "masculino") or 0)
    total_creados += (generar_partidos_por_genero(equipos_f, "femenino") or 0)

    print(f"Fixture de fase de grupos generado para {campeonato.nombre}. Total partidos creados: {total_creados}")
    return total_creados  # SIEMPRE int
