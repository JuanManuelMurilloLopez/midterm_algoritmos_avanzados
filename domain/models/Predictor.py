from algorithms.greedy import greedy_windows
from algorithms.rolling_hash import rolling_hash
from algorithms.lcs import longest_common_substring
from algorithms.kmp import kmp_contains 
from algorithms.z_function import z_relevance
from algorithms.z_function import z_function
from algorithms.rhythm import rhythm_score
from algorithms.dijkstra import dijkstra_explain

class Predictor:
    def __init__(self, window_size=5):
        self.window_size = window_size
    
    def z_relevance(pattern, form):
        if not pattern:
            return 0
        z = z_function(pattern + "#" + form)
        return max(z)


    def predict(self, teamA, teamB, graph=None):
        epsilon = 1 / self.window_size  
        
        candidate_pairs = []
        
        best_lcs = 0
        best_pattern = ""

        rhythm_A = rhythm_score(teamA.form[-self.window_size:])
        rhythm_B = rhythm_score(teamB.form[-self.window_size:])

        windowsA = greedy_windows(teamA.form, self.window_size)
        windowsB = greedy_windows(teamB.form, self.window_size)
        hashA = {}
        for w in windowsA:
            h_val, _ = rolling_hash(w)
            key = h_val[-1]              
            hashA.setdefault(key, []).append(w)

        for w in windowsB:
            h_val, _ = rolling_hash(w)
            h = h_val[-1]

            if h in hashA:
                for wa in hashA[h]:
                    candidate_pairs.append((wa, w))
        if not candidate_pairs:
            candidate_pairs = [(a, b) for a in windowsA for b in windowsB]

        for wA, wB in candidate_pairs:
            lcs_len, substring, _ = longest_common_substring(wA, wB)
            if lcs_len > best_lcs:
                best_lcs = lcs_len
                best_pattern = substring
        kmp_A, kmp_exp_A = kmp_contains(teamA.form, best_pattern)
        kmp_B, kmp_exp_B = kmp_contains(teamB.form, best_pattern)

        zA = z_relevance(best_pattern, teamA.form)
        zB = z_relevance(best_pattern, teamB.form)

        delta = rhythm_A - rhythm_B
        pattern_weight = best_lcs / self.window_size if best_lcs > 0 else 0
        adjusted_delta = delta * (1 + pattern_weight)
        epsilon = 1 / self.window_size

        if abs(adjusted_delta) < epsilon:
            winner = "DRAW"
        elif adjusted_delta > 0:
            winner = teamA.name
        else:
            winner = teamB.name

        if winner == "DRAW" and graph is not None:
            cost, _, _ = dijkstra_explain(
                graph,
                start=teamA.name,
                target=teamB.name
            )
            if cost < 0.9:
                winner = teamB.name


        explanation = {
            "teamA": teamA.name,
            "teamB": teamB.name,
            "rhythm_A": rhythm_A,
            "rhythm_B": rhythm_B,
            "winner": winner,
            "common_pattern": best_pattern,
            "lcs_length": best_lcs,
            "kmp_verified": {
                teamA.name: {
                    "found": kmp_A,
                    "details": kmp_exp_A
                },
                teamB.name: {
                    "found": kmp_B,
                    "details": kmp_exp_B
                }
            },
            "z_relevance": {
                teamA.name: zA,
                teamB.name: zB
            },
            "hash_filtered": True
        }


        return winner, explanation
    
    def get_winner(match):
        hg, ag = match["ft"]
        if hg > ag:
            return match["home"]
        elif ag > hg:
            return match["away"]
        else:
            return "DRAW"

