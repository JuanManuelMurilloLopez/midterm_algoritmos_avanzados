from domain.services.form import recent_form
from domain.models.Team import Team
from domain.models.Predictor import Predictor
from domain.services.loader import load_season_from_url
from domain.services.normalizaer import normalize_matches

URL = "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/en.1.json"

TEAM_A = "Fulham FC"
TEAM_B = "Chelsea FC"


def run_test(matches, description):
    formA = recent_form(matches, TEAM_A, n=15)
    formB = recent_form(matches, TEAM_B, n=15)

    teamA = Team(TEAM_A, formA)
    teamB = Team(TEAM_B, formB)

    predictor = Predictor(window_size=5)
    winner, explanation = predictor.predict(teamA, teamB)

    print("\n=== TEST:", description, "===")
    print("Winner:", winner)
    print("Rhythm A:", explanation["rhythm_A"])
    print("Rhythm B:", explanation["rhythm_B"])
    print("Pattern:", explanation["common_pattern"])


def test_remove_last_k(matches, k):
    reduced = matches[:-k]
    run_test(reduced, f"Remove last {k} matches")


def test_remove_random(matches, k):
    import random
    reduced = matches[:]
    for i in sorted(random.sample(range(len(matches)), k), reverse=True):
        reduced.pop(i)
    run_test(reduced, f"Remove {k} random matches")


if __name__ == "__main__":
    season = load_season_from_url(URL)
    matches = normalize_matches(season["matches"])

    test_remove_last_k(matches, 1)
    test_remove_last_k(matches, 3)
    test_remove_last_k(matches, 5)

    for i in range(3):
        test_remove_random(matches, 5)
