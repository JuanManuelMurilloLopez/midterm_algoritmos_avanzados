import pandas as pd

from domain.services.loader import load_season_from_url
from domain.services.normalizaer import normalize_matches

from experiments.experiment_base import run as run_base
from experiments.experiment_pattern import run as run_pattern
from experiments.experiment_pipeline import run as run_full

URL = "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/en.1.json"

print("Cargando datos...")
season = load_season_from_url(URL)
matches = normalize_matches(season["matches"])

experiments = {
    "baseline": run_base,
    "pattern": run_pattern,
    "pipeline": run_full
}

results_summary = []

for name, exp in experiments.items():
    print(f"\nEjecutando experimento: {name}")
    rows = exp(matches)

    df = pd.DataFrame(rows)
    accuracy = df["correct"].mean()

    df.to_csv(f"results_{name}.csv", index=False)

    results_summary.append({
        "model": name,
        "accuracy": accuracy,
        "samples": len(df)
    })

    print(f"Accuracy {name}: {accuracy:.3f}")

summary_df = pd.DataFrame(results_summary)
summary_df.to_csv("results_summary.csv", index=False)

print("\n=== RESUMEN FINAL ===")
print(summary_df)
