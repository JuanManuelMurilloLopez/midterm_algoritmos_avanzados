import random

def truncate_form(form, k):
    return form[:-k] if k < len(form) else ""

def random_remove(form, k):
    idx = list(range(len(form)))
    remove = set(random.sample(idx, min(k, len(form))))
    return "".join(form[i] for i in range(len(form)) if i not in remove)

def robustness_score(predictor, teamA, teamB, perturbations):
    base_winner, _ = predictor.predict(teamA, teamB)

    stable = 0
    total = 0

    for p in perturbations:
        formA_p = p(teamA.form)
        formB_p = p(teamB.form)

        if len(formA_p) < predictor.window_size or len(formB_p) < predictor.window_size:
            continue

        teamA_p = type(teamA)(teamA.name, formA_p)
        teamB_p = type(teamB)(teamB.name, formB_p)

        winner_p, _ = predictor.predict(teamA_p, teamB_p)

        total += 1
        if winner_p == base_winner:
            stable += 1

    return stable / total if total > 0 else 0
