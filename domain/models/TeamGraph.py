class TeamGraph:
    def __init__(self):
        self.adj = {}

    def add_team(self, team_name):
        if team_name not in self.adj:
            self.adj[team_name] = []

    def add_edge(self, from_team, to_team, weight, meta=None):
        self.add_team(from_team)
        self.add_team(to_team)

        self.adj[from_team].append({
            "to": to_team,
            "weight": weight,
            "meta": meta
        })
