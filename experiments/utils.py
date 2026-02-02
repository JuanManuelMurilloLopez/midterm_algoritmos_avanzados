from domain.services.form import recent_form
from domain.models.Team import Team
from domain.models.Predictor import Predictor

def run_inference(matches, predictor, window_size=5):
    rows = []

    for i in range(window_size, len(matches)):
        match = matches[i]
        past = matches[:i]

        home = match["home"]
        away = match["away"]

        form_home = recent_form(past, home, n=window_size)
        form_away = recent_form(past, away, n=window_size)

        if len(form_home) < window_size or len(form_away) < window_size:
            continue

        teamA = Team(home, form_home)
        teamB = Team(away, form_away)

        predicted, explanation = predictor.predict(teamA, teamB)
        actual = Predictor.get_winner(match)

        rows.append({
            "match": f"{home} vs {away}",
            "predicted": predicted,
            "actual": actual,
            "correct": predicted == actual
        })

    return rows
