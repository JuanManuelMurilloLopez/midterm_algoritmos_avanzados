import pandas as pd
from domain.services.loader import load_season_from_url
from domain.services.normalizaer import normalize_matches
from domain.services.form import recent_form
from domain.models.Team import Team
from domain.models.Predictor import Predictor
def actual_winner(match):
    hg, ag = match["ft"]
    if hg > ag:
        return match["home"]
    elif ag > hg:
        return match["away"]
    else:
        return "Draw"

WINDOW = 5

LEAGUES = {
    "EPL_2024": "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/en.1.json",
    "LA_LIGA_2024": "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/es.1.json",
    "BUNDESLIGA_2024": "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/de.1.json",
    "EPL_2023": "https://raw.githubusercontent.com/openfootball/football.json/master/2023-24/en.1.json",
    "LA_LIGA_2023": "https://raw.githubusercontent.com/openfootball/football.json/master/2023-24/es.1.json",
    "BUNDESLIGA_2023": "https://raw.githubusercontent.com/openfootball/football.json/master/2023-24/de.1.json",
}

def safe_matches(season):
    out = []
    for m in season["matches"]:
        score = m.get("score", {})
        ft = score.get("ft")
        if isinstance(ft, list) and len(ft) == 2:
            out.append({
                "home": m["team1"],
                "away": m["team2"],
                "ft": ft
            })
    return out


def evaluate_algorithmic_properties(predictor, matches):
    total = 0
    deterministic = 0
    explained = 0
    lcs_lengths = []
    stable = 0
    correct = 0   # <-- accuracy

    for i in range(WINDOW, len(matches)):
        match = matches[i]
        past = matches[:i]

        form_h = recent_form(past, match["home"], WINDOW)
        form_a = recent_form(past, match["away"], WINDOW)

        if len(form_h) < WINDOW or len(form_a) < WINDOW:
            continue

        team_h = Team(match["home"], form_h)
        team_a = Team(match["away"], form_a)

        # predicción
        winner, expl = predictor.predict(team_h, team_a)
        real = actual_winner(match)

        # --- accuracy empírica ---
        if winner == real:
            correct += 1

        # --- determinism ---
        w2, e2 = predictor.predict(team_h, team_a)
        if winner == w2 and expl["common_pattern"] == e2["common_pattern"]:
            deterministic += 1

        # --- explanation coverage ---
        if expl.get("common_pattern"):
            explained += 1
            lcs_lengths.append(len(expl["common_pattern"]))

        # --- local stability ---
        truncated_h = team_h.form[1:]
        truncated_a = team_a.form[1:]

        if len(truncated_h) >= WINDOW - 1 and len(truncated_a) >= WINDOW - 1:
            th = Team(match["home"], truncated_h)
            ta = Team(match["away"], truncated_a)
            w_trunc, _ = predictor.predict(th, ta)

            if w_trunc == winner:
                stable += 1

        total += 1

    return {
        "samples": total,
        "accuracy": round(correct / total, 3) if total else 0,
        "determinism_rate": round(deterministic / total, 3) if total else 0,
        "pattern_rate": round(explained / total, 3) if total else 0,
        "avg_lcs_length": round(sum(lcs_lengths) / len(lcs_lengths), 3) if lcs_lengths else 0,
        "local_stability": round(stable / total, 3) if total else 0
    }



def run_multi_league_tests():
    rows = []

    for league, url in LEAGUES.items():
        print(f"\n=== {league} ===")

        season = load_season_from_url(url)
        matches = safe_matches(season)

        predictor = Predictor(window_size=WINDOW)

        metrics = evaluate_algorithmic_properties(predictor, matches)
        metrics["league"] = league

        rows.append(metrics)

        print(metrics)

    df = pd.DataFrame(rows)
    df.to_csv("algorithmic_evaluation.csv", index=False)

    print("\n=== RESUMEN MULTI-LIGA ===")
    print(df)


if __name__ == "__main__":
    run_multi_league_tests()
