def result_for_team(match, team_name):
    home_goals, away_goals = match["ft"]

    if match["home"] == team_name:
        if home_goals > away_goals:
            return "W"
        elif home_goals < away_goals:
            return "L"
        return "D"

    if match["away"] == team_name:
        if away_goals > home_goals:
            return "W"
        elif away_goals < home_goals:
            return "L"
        return "D"

    return None


def recent_form(matches, team_name, n=5):
    results = []

    for match in reversed(matches):
        r = result_for_team(match, team_name)
        if r:
            results.append(r)
        if len(results) == n:
            break

    return "".join(reversed(results))
