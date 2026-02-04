import pandas as pd

from domain.services.multisport_loader import load_or_fetch
from domain.services.form import recent_form
from domain.models.Team import Team
from domain.models.Predictor import Predictor

WINDOW = 5
SEASON = 2024

SPORTS = {
    "football": {
        "url": "https://v3.football.api-sports.io/fixtures",
        "leagues": {
            "EPL": 39,
            "LaLiga": 140
        }
    },
    "hockey": {
        "url": "https://v1.hockey.api-sports.io/games",
        "leagues": {
            "NHL": 57
        }
    },
    "baseball": {
        "url": "https://v1.baseball.api-sports.io/games",
        "leagues": {
            "MLB": 1
        }
    }
}


def actual_winner(match):
    h, a = match["ft"]
    if h > a:
        return match["home"]
    elif a > h:
        return match["away"]
    else:
        return "DRAW"


def evaluate_algorithm(predictor, matches):
    correct, explained, total = 0, 0, 0

    for i in range(WINDOW, len(matches)):
        m = matches[i]
        past = matches[:i]

        fh = recent_form(past, m["home"], WINDOW)
        fa = recent_form(past, m["away"], WINDOW)

        if len(fh) < WINDOW or len(fa) < WINDOW:
            continue

        teamA = Team(m["home"], fh)
        teamB = Team(m["away"], fa)

        pred, explanation = predictor.predict(teamA, teamB)
        actual = actual_winner(m)

        total += 1
        if pred == actual:
            correct += 1
        if explanation.get("common_pattern"):
            explained += 1

    return (
        correct / total if total else 0,
        explained / total if total else 0,
        total
    )


def evaluate_ml(ml, matches, sport):
    correct, total = 0, 0

    for i in range(WINDOW, len(matches)):
        m = matches[i]
        past = matches[:i]

        fh = recent_form(past, m["home"], WINDOW)
        fa = recent_form(past, m["away"], WINDOW)

        if len(fh) < WINDOW or len(fa) < WINDOW:
            continue

        teamA = Team(m["home"], fh)
        teamB = Team(m["away"], fa)

        pred, _ = ml.predict(teamA, teamB, sport)
        actual = actual_winner(m)

        total += 1
        if pred == actual:
            correct += 1

    return correct / total if total else 0


def run_multisport():
    rows = []

    for sport, cfg in SPORTS.items():
        for league_name, league_id in cfg["leagues"].items():

            print(f"=== {sport.upper()} | {league_name} ===")

            matches = load_or_fetch(
                sport,
                league_name,
                {
                    "url": cfg["url"],
                    "league_id": league_id
                }
            )

            print("Matches:", len(matches))

            predictor = Predictor(window_size=WINDOW)

            alg_acc, coverage, total = evaluate_algorithm(predictor, matches)
           
            rows.append({
                "sport": sport,
                "league": league_name,
                "alg_accuracy": round(alg_acc, 3),
                "coverage": round(coverage, 3),
                "samples": total
            })

    df = pd.DataFrame(rows)
    print("\n=== MULTISPORT RESULTS ===")
    print(df)
    df.to_csv("multisport_results.csv", index=False)


if __name__ == "__main__":
    run_multisport()
