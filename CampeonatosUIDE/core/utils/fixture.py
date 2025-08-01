def generate_round_robin_fixture(teams):
    """
    Genera un fixture de tipo round-robin para una lista de equipos.
    Si el número de equipos es impar, se añade un 'BYE' para emparejar.
    """
    n = len(teams)
    if n % 2 != 0:
        teams.append("BYE")  # Añadir un equipo ficticio para número impar
        n += 1

    fixture = []
    # Crear una copia mutable de la lista de equipos
    temp_teams = list(teams)

    # Algoritmo Round-Robin
    for i in range(n - 1):
        round_matches = []
        for j in range(n // 2):
            team1 = temp_teams[j]
            team2 = temp_teams[n - 1 - j]
            if team1 != "BYE" and team2 != "BYE":
                round_matches.append((team1, team2))
        fixture.append(round_matches)

        # Rotar los equipos (mantener el primer equipo fijo)
        last_team = temp_teams.pop(n - 1)
        temp_teams.insert(1, last_team)
    
    return fixture
