from pruebas.robustness import robustness_score, truncate_form, random_remove

def run(predictor, teamA, teamB):
    perturbations = [
        lambda s: truncate_form(s, 1),
        lambda s: truncate_form(s, 3),
        lambda s: random_remove(s, 3),
        lambda s: random_remove(s, 5),
    ]

    return robustness_score(
        predictor,
        teamA,
        teamB,
        perturbations
    )
