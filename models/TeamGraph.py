from .Edge import Edge

class TeamGraph:
    def __init__(self):
        self.adj = {}

    def add_team(self, name):
        if name not in self.adj:
            self.adj[name] = []

    def cost(self, result):
        if result == "G":
            return 1.0
        if result == "E":
            return 2.0
        return 3.0

    def add_match(self, team_a, team_b, result_a):
        
        self.add_team(team_a)
        self.add_team(team_b)

        self.adj[team_a].append(
            Edge(
                to=team_b,
                weight=self.cost(result_a),
                meta={"result": result_a}
            )
        )

        if result_a == "G":
            inverse = "P"
        elif result_a == "P":
            inverse = "G"
        else:
            inverse = "E"

        self.adj[team_b].append(
            Edge(
                to=team_a,
                weight=self.cost(inverse),
                meta={"result": inverse}
            )
        )
