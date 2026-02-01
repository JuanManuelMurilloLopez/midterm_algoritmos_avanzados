from ..algorithms.lcs import longest_common_substring
from ..algorithms.lcs import predict_from_pattern
from ..algorithms.lcs import advantage_score
from ..algorithms.z_function import z_function
from ..algorithms.kmp import kmp_prefix_function

class Predictor:

    def compare_lcs(self, team_a, team_b):
        return longest_common_substring(
            team_a.results,
            team_b.results
        )

    def compare_z(self, team_a, team_b):
        combined = team_a.results + "#" + team_b.results
        return z_function(combined)

    def analyze_patterns(self, team):
        return kmp_prefix_function(team.results)
