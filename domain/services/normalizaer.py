def normalize_match(raw_match):
    return {
        "home": raw_match["team1"],
        "away": raw_match["team2"],
        "ft": raw_match["score"]["ft"]
    }


def normalize_matches(raw_matches):
    return [normalize_match(m) for m in raw_matches]
