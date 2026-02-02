from domain.services.loader import load_season_from_url
from domain.services.normalizaer import normalize_matches
from domain.services.form import recent_form
from domain.models.Team import Team
from domain.models.Predictor import Predictor

URL = "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/en.1.json"

season_data = load_season_from_url(URL)
matches = normalize_matches(season_data["matches"])

teamA_name = "Fulham FC"
teamB_name = "Chelsea FC"

formA = recent_form(matches, teamA_name, n=15)
formB = recent_form(matches, teamB_name, n=15)

teamA = Team(teamA_name, formA)
teamB = Team(teamB_name, formB)

predictor = Predictor(window_size=5)

score, explanation = predictor.predict(teamA, teamB)

print("=== PREDICCIÓN ===")
print("Score:", score)

print("\n=== EXPLICACIÓN ===")
for k, v in explanation.items():
    print(f"{k}: {v}")
