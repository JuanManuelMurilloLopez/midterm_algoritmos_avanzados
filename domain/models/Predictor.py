from algorithms.greedy import greedy_windows
from algorithms.lcs import longest_common_substring
from algorithms.rhythm import rhythm_score
from algorithms.explanation import explain_pattern


class Predictor:
    def __init__(self, window_size=5):
        self.window_size = window_size

    def predict(self, teamA, teamB):
        rhythm_A = rhythm_score(teamA.form[-self.window_size:])
        rhythm_B = rhythm_score(teamB.form[-self.window_size:])

        windowsA = greedy_windows(teamA.form, self.window_size)
        windowsB = greedy_windows(teamB.form, self.window_size)

        best_lcs = 0
        best_pattern = ""

        for wA in windowsA:
            for wB in windowsB:
                lcs_len, substring, _ = longest_common_substring(wA, wB)
                if lcs_len > best_lcs:
                    best_lcs = lcs_len
                    best_pattern = substring

        if rhythm_A > rhythm_B:
            winner = teamA.name
        elif rhythm_B > rhythm_A:
            winner = teamB.name
        else:
            winner = "Draw"

        explanation = {
            "teamA": teamA.name,
            "teamB": teamB.name,
            "rhythm_A": rhythm_A,
            "rhythm_B": rhythm_B,
            "common_pattern": best_pattern,
            "winner": winner,
            "message": (
                f"{winner} tiene mejor ritmo reciente "
                f"(A={rhythm_A:.2f}, B={rhythm_B:.2f}) "
                f"con patrón compartido '{best_pattern}'"
            )
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

