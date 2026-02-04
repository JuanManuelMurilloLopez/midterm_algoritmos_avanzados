import os
import requests
import pandas as pd

import ast

API_KEY = "2c2c9404e752f03de3d3026da8552fcf"
HEADERS = {"x-apisports-key": API_KEY}
SEASON = 2024
CACHE_DIR = "cache_api"

os.makedirs(CACHE_DIR, exist_ok=True)


def load_or_fetch(sport, league_name, cfg):
    path = f"{CACHE_DIR}/{sport}_{league_name}.csv"

    if os.path.exists(path):
        try:
            df = pd.read_csv(path)

            if df.empty:
                raise ValueError("Empty cache")

            df["ft"] = df["ft"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )

            return df.to_dict("records")

        except Exception:
            pass
    r = requests.get(
        cfg["url"],
        headers=HEADERS,
        params={"league": cfg["league_id"], "season": SEASON}
    )
    r.raise_for_status()

    matches = []

    for g in r.json()["response"]:
        if sport == "football":
            if g["fixture"]["status"]["short"] != "FT":
                continue
            h = g["goals"]["home"]
            a = g["goals"]["away"]

        elif sport in ["basketball", "baseball"]:
            if g["status"]["short"] != "FT":
                continue
            h = g["scores"]["home"]["total"]
            a = g["scores"]["away"]["total"]

        elif sport == "hockey":
            if g["status"]["short"] != "FT":
                continue
            h = g["scores"]["home"]
            a = g["scores"]["away"]

        else:
            continue

        if h is None or a is None:
            continue

        matches.append({
            "home": g["teams"]["home"]["name"],
            "away": g["teams"]["away"]["name"],
            "ft": [h, a]
        })

    pd.DataFrame(matches).to_csv(path, index=False)
    return matches
