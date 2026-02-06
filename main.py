from domain.services.loader import load_season_from_url
from domain.services.normalizaer import normalize_matches
from domain.services.form import recent_form
from domain.services.data_analysis import print_analysis 
from domain.services.data_analysis import generate_csv
from domain.models.Team import Team
from domain.models.Predictor import Predictor
import time
import tracemalloc
from domain.services.build_graph import build_team_graph
from algorithms.dijkstra import dijkstra_explain
import pandas as pd
from pruebas.fairness import rhythm_gap_fairness
from domain.services.Benchmark import Benchmark


URL = "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/en.1.json"

results_benchmark_pipeline = []
results_benchmark_predictor = []
bench = Benchmark(
    script_name="main.py",
    experiment_name="single_match_prediction",
    samples=1
)
bench.start()
season_data = load_season_from_url(URL)

bench.stop()

results_benchmark_pipeline.append(bench.result())
bench = Benchmark(
    script_name="main.py",
    experiment_name="single_match_prediction",
    samples=1
)
bench.start()
matches = normalize_matches(season_data["matches"])

bench.stop()
results_benchmark_pipeline.append(bench.result())
lenght = 5
results_rows = []


teams = set()

teamA_name = "Arsenal FC"
teamB_name = "Chelsea FC"

bench = Benchmark(
    script_name="main.py",
    experiment_name="single_match_prediction",
    samples=1
)
bench.start()
formA = recent_form(matches, teamA_name, n=5)
formB = recent_form(matches, teamB_name, n=5)

teamA = Team(teamA_name, formA)
teamB = Team(teamB_name, formB)

bench.stop()
results_benchmark_pipeline.append(bench.result())

bench = Benchmark(
    script_name="main.py",
    experiment_name="single_match_prediction",
    samples=1
)
bench.start()
predictor = Predictor(window_size=5)

score, explanation = predictor.predict(teamA, teamB)
bench.stop()
results_benchmark_predictor.append(bench.result())

print("\n=== EXPLICACIÓN PARA UN ENFRENTAMIENTO ===")
bench = Benchmark(
    script_name="Muestra de explicación para un enfrentamiento específico",
    experiment_name="single_match_prediction",
    samples=1
)
bench.start()
for k, v in explanation.items():
    print(f"{k}: {v}")

bench.stop()
results_benchmark_pipeline.append(bench.result())
print("\n=== INFERENCIA PROSPECTIVA ===")

bench = Benchmark(
    script_name="main.py",
    experiment_name="single_match_prediction",
    samples=1
)
bench.start()

for i in range(lenght, len(matches)):
    match = matches[i]

    home = match["home"]
    away = match["away"]
    past_matches = matches[:i]

    form_home = recent_form(past_matches, home, n=5)
    form_away = recent_form(past_matches, away, n=5)

    if len(form_home) < 5 or len(form_away) < 5:
        continue

    team_home = Team(home, form_home)
    team_away = Team(away, form_away)
    bench = Benchmark(
        script_name="main.py",
        experiment_name="single_match_prediction",
        samples=1
    )
    bench.start()
    score, explanation = predictor.predict(team_home, team_away)
    bench.stop()
    results_benchmark_predictor.append(bench.result())
    predicted = explanation["winner"]
    actual = Predictor.get_winner(match)

    hit = predicted == actual

    results_rows.append({
        "match": f"{home} vs {away}",
        "predicted_winner": predicted,
        "actual_winner": actual,
        "correct": hit,
        "rhythm_home": explanation["rhythm_A"],
        "rhythm_away": explanation["rhythm_B"],
        "common_pattern": explanation["common_pattern"]
    })

bench.stop()
results_benchmark_pipeline.append(bench.result())


for m in matches:
    teams.add(m["home"])
    teams.add(m["away"])

bench = Benchmark(
    script_name="main.py",
    experiment_name="single_match_prediction",
    samples=1
)
bench.start()
graph = build_team_graph(matches, teams)

cost, path, explanation = dijkstra_explain(
    graph,
    start="Fulham FC",
    target="Chelsea FC"
)
bench.stop()
results_benchmark_pipeline.append(bench.result())
print("\n=== DIJKSTRA ===")
print("Costo total:", round(cost, 3))
print("Camino óptimo:", " → ".join(path))

print("\n=== EXPLICACIÓN DEL CAMINO ===")
for e in explanation:
    print(
        f"{e['from']} → {e['to']} | "
        f"costo={round(e['edge_cost'],3)} | "
        f"{e['reason']}"
    )


generate_csv(results_rows)

df = pd.read_csv("results_inference.csv")
fairness = rhythm_gap_fairness(df, threshold=1/5)


print_analysis(df)
print("Fairness:", fairness)

print("\n=== BENCHMARK: PIPELINE GENERAL ===")
df_pipeline = pd.DataFrame(results_benchmark_pipeline)
print(df_pipeline)

print("\n=== BENCHMARK: PREDICTOR ===")
df_predictor = pd.DataFrame(results_benchmark_predictor)
print(df_predictor)
