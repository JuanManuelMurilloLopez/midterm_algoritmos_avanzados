def explain_pattern(teamA, teamB, pattern, score):
    return {
        "teamA": teamA.name,
        "teamB": teamB.name,
        "pattern": pattern,
        "score": score,
        "message": f"Ambos equipos comparten el patrón {pattern}"
    }