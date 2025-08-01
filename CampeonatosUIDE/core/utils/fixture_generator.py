import math

def generate_round_robin_fixture(teams):
    n = len(teams)
    if n < 2:
        return []

    # If odd number of teams, add a dummy team
    if n % 2 != 0:
        teams.append("BYE")  # Represents a bye week
        n += 1

    fixture = []
    rounds = n - 1

    for r in range(rounds):
        current_round = []
        for i in range(n // 2):
            team1 = teams[i]
            team2 = teams[n - 1 - i]

            if team1 != "BYE" and team2 != "BYE":
                # Ensure each team plays home and away
                if r % 2 == 0:  # Even rounds: team1 home, team2 away
                    current_round.append((team1, team2))
                else:  # Odd rounds: team2 home, team1 away
                    current_round.append((team2, team1))
        fixture.append(current_round)

        # Rotate teams (except the first one)
        first_team = teams[0]
        last_team = teams.pop()
        teams.insert(1, last_team)
        teams[0] = first_team

    return fixture
