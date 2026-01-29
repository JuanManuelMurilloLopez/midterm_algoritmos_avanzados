# Función para priorizar los partidos recientes (Greedy)
def greedy_select_recent(results, k):
    selected = results[-k:]

    explanation = {
        "algorithm": "Greedy Selection",
        "criterion": "most recent matches",
        "selected_matches": selected
    }

    return selected, explanation