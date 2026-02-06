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
SPORT_SAMPLE_SIZE = 2500
GLOBAL_SAMPLE_SIZE = 2600
NUM_RANDOM_SPORTS = 2
NUM_RUNS = 5


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

def run_multisport_ml_by_sport():
    """
    Ejecuta un análisis ML por deporte usando 5000 samples agregados
    de todas sus ligas.
    """

    rows = []

    for sport, cfg in SPORTS.items():
        print(f"\n===== ANALYSIS BY SPORT | {sport.upper()} =====")

        all_dfs = []

        # 1️⃣ Juntar datos de todas las ligas del deporte
        for league, league_id in cfg["leagues"].items():
            print(f"Loading {league}...")

            matches = load_or_fetch(
                sport,
                league,
                {"url": cfg["url"], "league_id": league_id}
            )

            df = extract_features(matches)
            if len(df) >= 50:
                all_dfs.append(df)

        if not all_dfs:
            print("No sufficient data for this sport")
            continue

        full_df = pd.concat(all_dfs, ignore_index=True)

        # 2️⃣ Sampleo fijo de 5000 (o menos si no alcanza)
        if len(full_df) > SPORT_SAMPLE_SIZE:
            full_df = full_df.sample(
                n=SPORT_SAMPLE_SIZE,
                random_state=RANDOM_STATE
            )

        print(f"Total samples used: {len(full_df)}")

        X = full_df.drop(columns=["label"])
        y = full_df["label"]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        split = int(len(X_scaled) * (1 - TEST_RATIO))
        X_train, X_test = X_scaled[:split], X_scaled[split:]
        y_train, y_test = y.iloc[:split], y.iloc[split:]

        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            class_weight="balanced",
            random_state=RANDOM_STATE
        )

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)

        print(f"[{sport.upper()}] Accuracy (5000 samples): {acc:.3f}")

        rows.append({
            "sport": sport,
            "samples": len(full_df),
            "ml_binary_accuracy": round(acc, 3)
        })

    summary = pd.DataFrame(rows)
    print("\n=== MULTISPORT ML BY SPORT (5000 samples) ===")
    print(summary)

    summary.to_csv("multisport_ml_by_sport_5000.csv", index=False)

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
            X_scaled = scaler.fit_transform(X)

            split = int(len(X_scaled) * (1 - TEST_RATIO))
            X_train, X_test = X_scaled[:split], X_scaled[split:]
            y_train, y_test = y.iloc[:split], y.iloc[split:]

            model = RandomForestClassifier(
                n_estimators=300,
                max_depth=10,
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

def run_multisport_ml_global():
    """
    Ejecuta un análisis ML global usando todos los deportes juntos
    con un dataset fijo de 5000 samples.
    """

    print("\n===== GLOBAL MULTISPORT ANALYSIS =====")

    all_dfs = []

    # 1️⃣ Recolectar datos de todos los deportes y ligas
    for sport, cfg in SPORTS.items():
        print(f"\nCollecting data from sport: {sport.upper()}")

        for league, league_id in cfg["leagues"].items():
            print(f"  Loading {league}...")

            matches = load_or_fetch(
                sport,
                league,
                {"url": cfg["url"], "league_id": league_id}
            )

            df = extract_features(matches)

            if len(df) >= 50:
                all_dfs.append(df)
            else:
                print(f"  [SKIPPED] {league} ({len(df)} samples)")

    if not all_dfs:
        print("No sufficient data for global analysis")
        return

    full_df = pd.concat(all_dfs, ignore_index=True)

    # 2️⃣ Sample global fijo
    if len(full_df) > SPORT_SAMPLE_SIZE:
        full_df = full_df.sample(
            n=SPORT_SAMPLE_SIZE,
            random_state=RANDOM_STATE
        )

    print(f"\nTotal global samples used: {len(full_df)}")

    X = full_df.drop(columns=["label"])
    y = full_df["label"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    split = int(len(X_scaled) * (1 - TEST_RATIO))
    X_train, X_test = X_scaled[:split], X_scaled[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
        class_weight="balanced",
        random_state=RANDOM_STATE
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)

    print(f"\n[GLOBAL] Binary ML Accuracy (all sports): {acc:.3f}")

    summary = pd.DataFrame([{
        "scope": "global_all_sports",
        "samples": len(full_df),
        "ml_binary_accuracy": round(acc, 3)
    }])

    summary.to_csv("multisport_ml_global_5000.csv", index=False)
import random

def run_multisport_ml_random_sports():
    """
    Ejecuta múltiples corridas ML usando datos de deportes
    seleccionados aleatoriamente.
    """

    results = []

    sport_names = list(SPORTS.keys())

    for run in range(NUM_RUNS):
        print(f"\n===== RANDOM SPORT RUN {run+1} =====")

        # 1️⃣ Elegir deportes aleatorios
        chosen_sports = random.sample(sport_names, k=NUM_RANDOM_SPORTS)
        print(f"Selected sports: {chosen_sports}")

        all_dfs = []

        # 2️⃣ Recolectar datos solo de esos deportes
        for sport in chosen_sports:
            cfg = SPORTS[sport]

            for league, league_id in cfg["leagues"].items():
                matches = load_or_fetch(
                    sport,
                    league,
                    {"url": cfg["url"], "league_id": league_id}
                )

                df = extract_features(matches)
                if len(df) >= 50:
                    all_dfs.append(df)

        if not all_dfs:
            print("No data collected in this run")
            continue

        full_df = pd.concat(all_dfs, ignore_index=True)

        # 3️⃣ Sampleo global fijo
        if len(full_df) > GLOBAL_SAMPLE_SIZE:
            full_df = full_df.sample(
                n=GLOBAL_SAMPLE_SIZE,
                random_state=RANDOM_STATE + run
            )

        print(f"Samples used: {len(full_df)}")

        X = full_df.drop(columns=["label"])
        y = full_df["label"]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        split = int(len(X_scaled) * (1 - TEST_RATIO))
        X_train, X_test = X_scaled[:split], X_scaled[split:]
        y_train, y_test = y.iloc[:split], y.iloc[split:]

        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            class_weight="balanced",
            random_state=RANDOM_STATE + run
        )

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {acc:.3f}")

        results.append({
            "run": run + 1,
            "sports_used": ",".join(chosen_sports),
            "samples": len(full_df),
            "accuracy": round(acc, 3)
        })

    summary = pd.DataFrame(results)
    print("\n=== RANDOM SPORTS SUMMARY ===")
    print(summary)

    summary.to_csv("multisport_ml_random_sports.csv", index=False)

def run_multisport_ml_football_hockey():
    """
    Ejecuta un análisis ML usando únicamente football y hockey,
    combinando todas sus ligas en un solo dataset.
    """

    print("\n===== FOOTBALL + HOCKEY ANALYSIS =====")

    selected_sports = ["football", "hockey"]
    all_dfs = []

    # 1️⃣ Recolectar datos solo de football y hockey
    for sport in selected_sports:
        cfg = SPORTS[sport]
        print(f"\nCollecting data from {sport.upper()}")

        for league, league_id in cfg["leagues"].items():
            print(f"  Loading {league}...")

            matches = load_or_fetch(
                sport,
                league,
                {"url": cfg["url"], "league_id": league_id}
            )

            df = extract_features(matches)

            if len(df) >= 50:
                all_dfs.append(df)
            else:
                print(f"  [SKIPPED] {league} ({len(df)} samples)")

    if not all_dfs:
        print("No sufficient data for football + hockey analysis")
        return

    full_df = pd.concat(all_dfs, ignore_index=True)

    # 2️⃣ Sampleo global fijo
    if len(full_df) > GLOBAL_SAMPLE_SIZE:
        full_df = full_df.sample(
            n=GLOBAL_SAMPLE_SIZE,
            random_state=RANDOM_STATE
        )

    print(f"\nTotal samples used: {len(full_df)}")

    X = full_df.drop(columns=["label"])
    y = full_df["label"]
    X_scaled = X.values

    split = int(len(X_scaled) * (1 - TEST_RATIO))
    X_train, X_test = X_scaled[:split], X_scaled[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    model = RandomForestClassifier(
        n_estimators=500,
        max_depth=8,
        min_samples_leaf=10,
        class_weight="balanced",
        random_state=RANDOM_STATE
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)

    print(f"\n[FOOTBALL + HOCKEY] Binary ML Accuracy: {acc:.3f}")

    summary = pd.DataFrame([{
        "scope": "football_hockey",
        "sports": "football,hockey",
        "samples": len(full_df),
        "ml_binary_accuracy": round(acc, 3)
    }])

    summary.to_csv("multisport_ml_football_hockey.csv", index=False)


if __name__ == "__main__":
    #run_multisport_ml_by_sport()
    #run_multisport_ml_random_sports()
    #run_multisport_ml()
    #run_multisport_ml_global() 
    run_multisport_ml_football_hockey()