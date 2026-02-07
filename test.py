import pandas as pd
from domain.services.Benchmark import Benchmark
from domain.services.loader import load_season_from_url
from domain.services.normalizaer import normalize_matches
from domain.services.form import recent_form
from domain.models.Team import Team
from domain.models.Predictor import Predictor
from domain.models.TeamGraph import TeamGraph  

rows_benchmarks = []

def build_prestige_graph(matches):
    graph = TeamGraph()
    for m in matches:
        home = m["home"]
        away = m["away"]
        hg, ag = m["ft"]
        
        if hg > ag: 
            graph.add_edge(away, home, 1.0, meta={"result": "L"})
        elif ag > hg:
            graph.add_edge(home, away, 1.0, meta={"result": "L"})
        else: 
            graph.add_edge(home, away, 0.5, meta={"result": "D"})
            graph.add_edge(away, home, 0.5, meta={"result": "D"})
    return graph

def calculate_pagerank(graph, damping=0.85, iterations=20):
    nodes = set(graph.adj.keys())
    for neighbors in graph.adj.values():
        for edge in neighbors:
            nodes.add(edge["to"])
            
    if not nodes: return {}
    
    pagerank = {node: 1.0 for node in nodes}
    
    for _ in range(iterations):
        new_pagerank = {node: (1 - damping) for node in nodes}
        for node in nodes:
            outgoing = graph.adj.get(node, [])
            if not outgoing: continue
            
            share = pagerank[node] * damping / len(outgoing)
            for edge in outgoing:
                new_pagerank[edge["to"]] += share
        pagerank = new_pagerank
    return pagerank

def actual_winner(match):
    hg, ag = match["ft"]
    if hg > ag: return match["home"]
    elif ag > hg: return match["away"]
    else: return "Draw"

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
    """
    Params:
        season (dict): Temporada con lista de partidos crudos.

    Returns:
        list[dict]: Partidos normalizados con marcador final válido.
    """

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
    """
    Params:
        predictor (Predictor): Algoritmo explicable.
        matches (list[dict]): Partidos históricos.

    Returns:
        dict: Métricas algorítmicas (accuracy, estabilidad, determinismo, etc.).
    """

    total = 0
    
    deterministic = 0
    explained = 0
    stable = 0
    correct_lcs = 0
    lcs_lengths = []

    correct_pr = 0
    agreement = 0 

    for i in range(WINDOW, len(matches)):
        match = matches[i]
        past = matches[:i]

        form_h = recent_form(past, match["home"], WINDOW)
        form_a = recent_form(past, match["away"], WINDOW)

        if len(form_h) < WINDOW or len(form_a) < WINDOW:
            continue

        team_h = Team(match["home"], form_h)
        team_a = Team(match["away"], form_a)
        real = actual_winner(match)

        winner_lcs, expl = predictor.predict(team_h, team_a)
        
        if winner_lcs == real:
            correct_lcs += 1

        w2, e2 = predictor.predict(team_h, team_a)
        if winner_lcs == w2 and expl["common_pattern"] == e2["common_pattern"]:
            deterministic += 1
        if expl.get("common_pattern"):
            explained += 1
            lcs_lengths.append(len(expl["common_pattern"]))

        truncated_h = team_h.form[1:]
        truncated_a = team_a.form[1:]
        if len(truncated_h) >= WINDOW - 1:
            th = Team(match["home"], truncated_h)
            ta = Team(match["away"], truncated_a)
            w_trunc, _ = predictor.predict(th, ta)
            if w_trunc == winner_lcs:
                stable += 1

        pr_graph = build_prestige_graph(past)
        pr_scores = calculate_pagerank(pr_graph, iterations=15)
        
        score_h = pr_scores.get(match["home"], 0.15)
        score_a = pr_scores.get(match["away"], 0.15)
        
        if score_h > score_a: winner_pr = match["home"]
        elif score_a > score_h: winner_pr = match["away"]
        else: winner_pr = "Draw"

        if winner_pr == real:
            correct_pr += 1

        if winner_lcs == winner_pr:
            agreement += 1

        total += 1

    return {
        "samples": total,
        "acc_lcs": round(correct_lcs / total, 3) if total else 0,
        "acc_pagerank": round(correct_pr / total, 3) if total else 0,
        "agreement": round(agreement / total, 3) if total else 0, 
        "determinism": round(deterministic / total, 3) if total else 0,
        "stability": round(stable / total, 3) if total else 0,
        "avg_lcs_len": round(sum(lcs_lengths) / len(lcs_lengths), 3) if lcs_lengths else 0
    }

bench_global = Benchmark(
    script_name="test.py",
    experiment_name="multi_league_full_test",
    samples=len(LEAGUES)
)

bench_global.start()

def run_multi_league_tests():
    """
    Params:
        None

    Returns:
        None: Ejecuta evaluación algorítmica en múltiples ligas y exporta CSV.
    """

    rows = []
    print(f"{'League':<15} | {'LCS Acc':<8} | {'PR Acc':<8} | {'Agree':<8} | {'Samples'}")
    print("-" * 60)

    for league, url in LEAGUES.items():
        bench = Benchmark(
            script_name="test.py",
            experiment_name=f"load_season_{league}",
            samples=6
        )

        bench.start()

        season = load_season_from_url(url)
        bench.stop()
        rows_benchmarks.append(bench.result())
        bench = Benchmark(
                script_name="test.py",
                experiment_name=f"safe_matches_{league}",
                samples=len(season["matches"])
            )
        bench.start()
        matches = safe_matches(season)
        bench.stop()
        rows_benchmarks.append(bench.result())
        bench = Benchmark(
                script_name="test.py",
                experiment_name=f"Predictor_init_{league}",
                samples=len(season["matches"])
            )
        bench.start()
        predictor = Predictor(window_size=WINDOW)
        bench.stop()
        rows_benchmarks.append(bench.result())
        bench = Benchmark(
                script_name="test.py",
                experiment_name=f"Evaluation of Algorithmic{league}",
                samples=len(matches)
            )
        bench.start()
        metrics = evaluate_algorithmic_properties(predictor, matches)
        bench.stop()
        rows_benchmarks.append(bench.result())
        metrics["league"] = league
        rows.append(metrics)

        print(f"{league:<15} | {metrics['acc_lcs']:<8} | {metrics['acc_pagerank']:<8} | {metrics['agreement']:<8} | {metrics['samples']}")

    df = pd.DataFrame(rows)
    bench_global.stop()
    rows_benchmarks.append(bench.result())

    df.to_csv("algorithmic_evaluation_with_pagerank.csv", index=False)
    print("\nResultados guardados en 'algorithmic_evaluation_with_pagerank.csv'")

    df_bench = pd.DataFrame(rows_benchmarks)
    df_bench.to_csv("benchmark_test_pipeline.csv", index=False)
    print("\nBenchmark guardado en 'benchmark_test_pipeline.csv'")
    print("\n=== BENCHMARK TEST PIPELINE (RAW) ===")
    print(df_bench)
    df_bench_summary = pd.DataFrame([{
        "mean_time_sec": df_bench["time_sec"].mean(),
        "median_time_sec": df_bench["time_sec"].median(),
        "mean_mem_current_mb": df_bench["mem_current_mb"].mean(),
        "median_mem_current_mb": df_bench["mem_current_mb"].median(),
        "mean_mem_peak_mb": df_bench["mem_peak_mb"].mean(),
        "median_mem_peak_mb": df_bench["mem_peak_mb"].median(),
        "runs": len(df_bench)
    }])

    print("\n=== BENCHMARK TEST PIPELINE (SUMMARY: MEAN & MEDIAN) ===")
    print(df_bench_summary)



if __name__ == "__main__":
    run_multi_league_tests()