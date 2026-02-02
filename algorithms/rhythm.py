def rhythm_score(form):
    values = {"W": 1, "D": 0, "L": -1}
    if not form:
        return 0.0
    total = sum(values[c] for c in form)
    return total / len(form)
