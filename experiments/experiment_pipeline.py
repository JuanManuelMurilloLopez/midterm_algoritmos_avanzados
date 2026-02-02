from experiments.utils import run_inference
from domain.models.Predictor import Predictor
from domain.services.build_graph import build_team_graph

def run(matches):
    teams = set()
    for m in matches:
        teams.add(m["home"])
        teams.add(m["away"])

    graph = build_team_graph(matches, teams)

    predictor = Predictor(
        window_size=5
    )

    return run_inference(matches, predictor)
