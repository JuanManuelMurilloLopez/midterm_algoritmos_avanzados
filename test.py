import random
import pandas as pd
from domain.services.loader import load_season_from_url
from domain.services.normalizaer import normalize_matches
from domain.services.form import recent_form
from domain.models.Team import Team
from domain.models.Predictor import Predictor
from pruebas.robustness import truncate_form, random_remove, robustness_score

WINDOW = 5

LEAGUES = {
    "EPL_2024": "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/en.1.json",
    "LA_LIGA_2024": "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/es.1.json",
    "BUNDESLIGA_2024": "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/de.1.json",
    "EPL_2023": "https://raw.githubusercontent.com/openfootball/football.json/master/2023-24/en.1.json",
    "LA_LIGA_2023": "https://raw.githubusercontent.com/openfootball/football.json/master/2023-24/es.1.json",
    "BUNDESLIGA_2023": "https://raw.githubusercontent.com/openfootball/football.json/master/2023-24/de.1.json",
    "EPL_2022": "https://raw.githubusercontent.com/openfootball/football.json/master/2022-23/en.1.json",
    "LA_LIGA_2022": "https://raw.githubusercontent.com/openfootball/football.json/master/2022-23/es.1.json",
    "BUNDESLIGA_2022": "https://raw.githubusercontent.com/openfootball/football.json/master/2022-23/de.1.json",
}

PERTURBATIONS = [
    lambda s: truncate_form(s, 1),
    lambda s: truncate_form(s, 3),
    lambda s: truncate_form(s, 5),
    lambda s: random_remove(s, 3),
    lambda s: random_remove(s, 5),
]

def safe_normalize_matches(raw_matches):
    normalized = []

    for m in raw_matches:
        score = m.get("score", {})

        # solo aceptamos ft bien formado
        ft = score.get("ft")
        if not isinstance(ft, list) or len(ft) != 2:
            continue

        normalized.append({
            "home": m["team1"],
            "away": m["team2"],
            "ft": ft
        })

    return normalized


def filter_finished_matches(matches):
    filtered = []
    for m in matches:
        if "ft" in m and isinstance(m["ft"], list) and len(m["ft"]) == 2:
            filtered.append(m)
    return filtered


def actual_winner(match):
    hg, ag = match["ft"]
    if hg > ag:
        return match["home"]
    elif ag > hg:
        return match["away"]
    else:
        return "Draw"


def evaluate_model(predictor, matches):
    correct = 0
    explained = 0
    total = 0

    for i in range(WINDOW, len(matches)):
        match = matches[i]
        past = matches[:i]

        home = match["home"]
        away = match["away"]

        form_h = recent_form(past, home, WINDOW)
        form_a = recent_form(past, away, WINDOW)

        if len(form_h) < WINDOW or len(form_a) < WINDOW:
            continue

        team_h = Team(home, form_h)
        team_a = Team(away, form_a)

        winner, explanation = predictor.predict(team_h, team_a)
        actual = actual_winner(match)

        total += 1
        if winner == actual:
            correct += 1

        if explanation.get("common_pattern"):
            explained += 1

    accuracy = correct / total if total else 0
    coverage = explained / total if total else 0

    return accuracy, coverage, total


def evaluate_robustness(predictor, matches, samples=40):
    scores = []

    valid_matches = matches[WINDOW:]
    if len(valid_matches) < samples:
        samples = len(valid_matches)

    sampled = random.sample(valid_matches, samples)

    for match in sampled:
        idx = matches.index(match)
        past = matches[:idx]

        form_h = recent_form(past, match["home"], WINDOW)
        form_a = recent_form(past, match["away"], WINDOW)

        if len(form_h) < WINDOW or len(form_a) < WINDOW:
            continue

        team_h = Team(match["home"], form_h)
        team_a = Team(match["away"], form_a)

        r = robustness_score(
            predictor,
            team_h,
            team_a,
            PERTURBATIONS
        )
        scores.append(r)

    return sum(scores) / len(scores) if scores else 0


def run_multi_league_experiments():
    summary = []

    for league_name, url in LEAGUES.items():
        print(f"\n=== LIGA: {league_name} ===")

        season = load_season_from_url(url)
        matches = safe_normalize_matches(season["matches"])

        print(f"Partidos válidos: {len(matches)}")

        predictor = Predictor(window_size=WINDOW)

        acc, cov, total = evaluate_model(predictor, matches)
        rob = evaluate_robustness(predictor, matches)

        summary.append({
            "league": league_name,
            "accuracy": round(acc, 3),
            "robustness": round(rob, 3),
            "coverage": round(cov, 3),
            "samples": total
        })


    df = pd.DataFrame(summary)
    df.to_csv("multi_league_results.csv", index=False)

    print("\n=== RESUMEN MULTI-LIGA ===")
    print(df)


if __name__ == "__main__":
    run_multi_league_experiments()
