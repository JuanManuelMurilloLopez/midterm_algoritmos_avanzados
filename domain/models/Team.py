from algorithms.rhythm import rhythm_score

class Team:
    def __init__(self, name, form):
        self.name = name
        self.form = form
        self.rhythm = rhythm_score(form)

    def __repr__(self):
        return f"{self.name} (rhythm={self.rhythm:.2f})"
