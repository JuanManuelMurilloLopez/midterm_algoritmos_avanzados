from experiments.utils import run_inference
from domain.models.Predictor import Predictor

def run(matches):
    predictor = Predictor(
        window_size=5,
    )
    return run_inference(matches, predictor)
