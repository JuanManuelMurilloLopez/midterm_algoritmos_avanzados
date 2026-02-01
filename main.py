import requests

def normalize_match(raw_match):
    return {
        "home": raw_match["team1"],
        "away": raw_match["team2"],
        "ft": raw_match["score"]["ft"]
    }

def result_for_team(match, team_name):
    home_goals, away_goals = match["ft"]

    if match["home"] == team_name:
        if home_goals > away_goals:
            return "W"
        elif home_goals < away_goals:
            return "L"
        else:
            return "D"

    if match["away"] == team_name:
        if away_goals > home_goals:
            return "W"
        elif away_goals < home_goals:
            return "L"
        else:
            return "D"

    return None  # el equipo no participó
def recent_form(matches, team_name, n=5):
    results = []

    # recorrer del más reciente al más viejo
    for match in reversed(matches):
        r = result_for_team(match, team_name)
        if r:
            results.append(r)
        if len(results) == n:
            break

    return "".join(reversed(results))  # orden cronológico

url = "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/es.1.json"
data = requests.get(url).json()
print("Datos de la temporada:", data)
matches = [normalize_match(m) for m in data["matches"]]


teamA = "Fulham FC"
teamB = "Chelsea FC"

formA = recent_form(matches, teamA, n=15)
formB = recent_form(matches, teamB, n=15)

print("teamA:", formA)
print("teamB:", formB)
