# def generar_sorteo_eliminacion_simple(equipos):
#     """
#     Genera un sorteo de eliminación simple para una lista de equipos.
#     La primera ronda usa nombres reales. Las siguientes usan "Ganador de (...)"
#     """
#     if len(equipos) % 2 != 0:
#         equipos.append("BYE")

#     sorteos = []
#     ronda_actual = list(equipos)

#     while len(ronda_actual) > 1:
#         ronda = []
#         siguiente_ronda = []

#         i = 0
#         while i < len(ronda_actual):
#             equipo1 = ronda_actual[i]
#             equipo2 = ronda_actual[i+1] if i+1 < len(ronda_actual) else "BYE"

#             if equipo1 == "BYE":
#                 ganador = equipo2
#             elif equipo2 == "BYE":
#                 ganador = equipo1
#             else:
#                 ganador = f"Ganador de ({equipo1} vs {equipo2})"
#                 ronda.append((equipo1, equipo2))

#             siguiente_ronda.append(ganador)
#             i += 2

#         if ronda:  # Solo agregamos rondas con partidos reales
#             sorteos.append(ronda)

#         ronda_actual = siguiente_ronda

#     return sorteos


# # Prueba
# equipos = ["Equipo A", "Equipo B", "Equipo C", "Equipo D", "Equipo E"]
# encuentros = generar_sorteo_eliminacion_simple(equipos)

# for i, ronda in enumerate(encuentros, start=1):
#     print(f"Ronda {i}:")
#     for match in ronda:
#         print(f"  - {match[0]} vs {match[1]}")
