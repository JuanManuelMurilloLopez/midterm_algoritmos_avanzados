import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

from domain.services.multisport_loader import load_or_fetch
from domain.services.form import recent_form
from domain.models.Team import Team
from domain.models.Predictor import Predictor
from domain.models.TeamGraph import TeamGraph

WINDOW = 5
TEST_RATIO = 0.1
RANDOM_STATE = 42

SPORTS = {
    "football": {
        "url": "https://v3.football.api-sports.io/fixtures",
        "leagues": {
           "EPL": 39,
            "LaLiga": 140,
            "SerieA": 135,
            "Ligue1": 61,
            "Bundesliga": 78,
        "Eredivisie": 88,
        "PrimeiraLiga": 94,
        "LigaMX": 262,
        "MLS": 253,
        "BrasileiraoA": 71,
        }
    },
    "baseball": {
        "url": "https://v1.baseball.api-sports.io/games",
        "leagues": {
            "MLB": 1,
            "NPB": 3,
            "KBO": 5,
            "LMB": 2,
            "CPBL": 6
        }
    },
    "hockey": {
        "url": "https://v1.hockey.api-sports.io/games",
        "leagues": {
            "NHL": 57,
            "AHL": 58,
            "ECHL": 59,
            "OHL": 60,
            "WHL": 62,
        }
    }
}

def binary_outcome(match):
    """
    Params:
        match (dict): Partido con clave "ft" = [home_score, away_score].

    Returns:
        int | None: 1 si gana home, -1 si gana away, None si empate.
    """

    h, a = match["ft"]
    if h > a:
        return 1
    elif a > h:
        return -1
    else:
        return None


def build_prestige_graph(matches):
    """
    Params:
        matches (list[dict]): Lista de partidos históricos con claves "home", "away" y "ft".

    Returns:
        TeamGraph: Grafo dirigido que representa victorias como aristas ponderadas.
    """

    graph = TeamGraph()
    for m in matches:
        h, a = m["home"], m["away"]
        hg, ag = m["ft"]
        if hg > ag:
            graph.add_edge(a, h, 1.0)
        elif ag > hg:
            graph.add_edge(h, a, 1.0)
    return graph



def calculate_pagerank(graph, damping=0.85, iterations=20):
    """
    Params:
        graph (TeamGraph): Grafo de equipos con aristas dirigidas.
        damping (float): Factor de amortiguamiento de PageRank.
        iterations (int): Número de iteraciones.

    Returns:
        dict[str, float]: Puntaje PageRank por equipo.
    """

    nodes = set(graph.adj.keys())
    for edges in graph.adj.values():
        for e in edges:
            nodes.add(e["to"])
    if not nodes:
        return {}

    pr = {n: 1.0 for n in nodes}
    for _ in range(iterations):
        new_pr = {n: (1 - damping) for n in nodes}
        for n in nodes:
            outs = graph.adj.get(n, [])
            if not outs:
                continue
            share = pr[n] * damping / len(outs)
            for e in outs:
                new_pr[e["to"]] += share
        pr = new_pr
    return pr

def extract_features(matches):
    """
    Params:
        matches (list[dict]): Lista ordenada temporalmente de partidos.

    Returns:
        pandas.DataFrame: Features explicables por partido y etiqueta binaria.
    """

    predictor = Predictor(window_size=WINDOW)
    rows = []

    for i in range(WINDOW + 10, len(matches)):
        m = matches[i]
        outcome = binary_outcome(m)
        if outcome is None:
            continue

        past = matches[:i]
        fh = recent_form(past, m["home"], WINDOW)
        fa = recent_form(past, m["away"], WINDOW)
        if len(fh) < WINDOW or len(fa) < WINDOW:
            continue

        teamH = Team(m["home"], fh)
        teamA = Team(m["away"], fa)

        _, expl = predictor.predict(teamH, teamA)

        graph = build_prestige_graph(past)
        pr = calculate_pagerank(graph)

        rows.append({
            "rhythm_gap": expl["rhythm_A"] - expl["rhythm_B"],
            "lcs_length": expl["lcs_length"],
            "pattern_weight": expl["lcs_length"] / WINDOW,
            "pr_gap": pr.get(m["home"], 0.0) - pr.get(m["away"], 0.0),
            "label": outcome
        })

    return pd.DataFrame(rows)

def run_multisport_ml():
    """
    Params:
        None

    Returns:
        None: Ejecuta entrenamiento y evaluación multi-deporte y guarda resultados.
    """

    rows = []

    for sport, cfg in SPORTS.items():
        for league, league_id in cfg["leagues"].items():
            print(f"\n=== {sport.upper()} | {league} ===")

            matches = load_or_fetch(
                sport,
                league,
                {"url": cfg["url"], "league_id": league_id}
            )

            df = extract_features(matches)
            if len(df) < 80:
                print("Datos insuficientes")
                continue

            X = df.drop(columns=["label"])
            y = df["label"]

            scaler = StandardScaler()
            X_scaled = X.values


            split = int(len(X_scaled) * (1 - TEST_RATIO))
            X_train, X_test = X_scaled[:split], X_scaled[split:]
            y_train, y_test = y.iloc[:split], y.iloc[split:]

            model = RandomForestClassifier(
                n_estimators=500,
                max_depth=6,
                min_samples_leaf=10,
                class_weight="balanced",
                random_state=RANDOM_STATE
            )


            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            acc = accuracy_score(y_test, y_pred)

            print(f"Binary ML Accuracy: {acc:.3f}")

            rows.append({
                "sport": sport,
                "league": league,
                "samples": len(df),
                "ml_binary_accuracy": round(acc, 3)
            })

    summary = pd.DataFrame(rows)
    print("\n=== MULTISPORT ML (BINARY) ===")
    print(summary)
    summary.to_csv("multisport_ml_binary.csv", index=False)


if __name__ == "__main__":
    run_multisport_ml()
