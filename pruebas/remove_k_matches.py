from domain.services.form import recent_form

def test_remove_last_k(matches, teamA, teamB, k):
    reduced = matches[:-k]
    formA = recent_form(reduced, teamA, n=15)
    formB = recent_form(reduced, teamB, n=15)
    return formA, formB
