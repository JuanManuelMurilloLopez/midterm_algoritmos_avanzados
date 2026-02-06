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
        """
        Params:
            pattern (str): Patrón a evaluar.
            form (str): Secuencia completa de resultados del equipo.

        Returns:
            int: Valor máximo de relevancia basado en la función Z.
        """
        if not pattern:
            return 0
        z = z_function(pattern + "#" + form)
        return max(z)

    def filter_hashing_table(self, windowsA, windowsB):
        """
        Params:
            windowsA (list[str]): Ventanas temporales del equipo A.
            windowsB (list[str]): Ventanas temporales del equipo B.

        Returns:
            list[tuple[str, str]]: Pares candidatos de ventanas para comparación.
        """
        hashA = {}
        candidate_pairs = []
        
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
        return candidate_pairs

    def search_best_pattern(self, candidate_pairs):
        """
            Params:
                candidate_pairs (list[tuple[str, str]]): Pares de ventanas candidatas.

            Returns:
                tuple[str, int]: Mejor patrón común encontrado y su longitud (LCS).
            """
        best_lcs = 0
        best_pattern = ""
        for wA, wB in candidate_pairs:
            lcs_len, substring, _ = longest_common_substring(wA, wB)
            if lcs_len > best_lcs:
                best_lcs = lcs_len
                best_pattern = substring
        return best_pattern, best_lcs
    
    def adjusted_delta(self,rhythm_A, rhythm_B, best_lcs, window_size):
        """
           Params:
                rhythm_A (float): Ritmo del equipo A.
                rhythm_B (float): Ritmo del equipo B.
                best_lcs (int): Longitud del mejor patrón común encontrado.
                window_size (int): Tamaño de la ventana usada para normalización.

            Returns:
                float: Diferencia de ritmo ajustada por el peso del patrón.
            """
        delta = rhythm_A - rhythm_B
        pattern_weight = best_lcs / window_size if best_lcs > 0 else 0
        adjusted_delta = delta * (1 + pattern_weight)
        return adjusted_delta
    
    def remove_draws_graph(self,winner, teamA_name, teamB_name, graph):
        """
        Params:
            adjusted_delta (float): Diferencia de ritmo ajustada.
            teamA_name (str): Nombre del equipo A.
            teamB_name (str): Nombre del equipo B.
            window_size (int): Tamaño de la ventana (define el umbral epsilon).

        Returns:
            str: Nombre del equipo ganador o "DRAW".
        """
        if winner == "DRAW" and graph is not None:
            cost, _, _ = dijkstra_explain(
                graph,
                start=teamA_name,
                target=teamB_name
            )
            if cost < 0.9:
                return teamB_name

        return winner


    def get_primary_winner(self,adjusted_delta, teamA_name, teamB_name, window_size):
        """
        Params:
            winner (str): Resultado preliminar ("DRAW" o nombre del equipo).
            teamA_name (str): Nombre del equipo A.
            teamB_name (str): Nombre del equipo B.
            graph (TeamGraph | None): Grafo histórico para desempate.

        Returns:
            str: Resultado final tras aplicar el desempate por grafo.
        """
        epsilon = 1 / window_size

        if abs(adjusted_delta) < epsilon:
            return "DRAW"
        elif adjusted_delta > 0:
            return teamA_name
        else:
            return teamB_name


    def predict(self, teamA, teamB, graph=None):
        """
        Params:
            teamA (Team): Equipo local.
            teamB (Team): Equipo visitante.
            graph (TeamGraph | None): Grafo opcional para desempate.

        Returns:
            tuple[str, dict]: Equipo ganador estimado y explicación estructurada.
        """

        epsilon = 1 / self.window_size  
    

        rhythm_A = rhythm_score(teamA.form[-self.window_size:])
        rhythm_B = rhythm_score(teamB.form[-self.window_size:])

        windowsA = greedy_windows(teamA.form, self.window_size)
        windowsB = greedy_windows(teamB.form, self.window_size)
        
        candidate_pairs = self.filter_hashing_table(windowsA, windowsB)

        best_pattern, best_lcs = self.search_best_pattern(candidate_pairs)
        
        kmp_A, kmp_exp_A = kmp_contains(teamA.form, best_pattern)
        kmp_B, kmp_exp_B = kmp_contains(teamB.form, best_pattern)

        zA = z_relevance(best_pattern, teamA.form)
        zB = z_relevance(best_pattern, teamB.form)

        adjusted_delta = self.adjusted_delta(
            rhythm_A,
            rhythm_B,
            best_lcs,
            self.window_size
        )

        winner = self.get_primary_winner(
            adjusted_delta,
            teamA.name,
            teamB.name,
            self.window_size
        )

        winner = self.remove_draws_graph(
            winner,
            teamA.name,
            teamB.name,
            graph
        )

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
        """
        Params:
            match (dict): Partido con marcador final.

        Returns:
            str: Nombre del equipo ganador o "DRAW".
        """

        hg, ag = match["ft"]
        if hg > ag:
            return match["home"]
        elif ag > hg:
            return match["away"]
        else:
            return "DRAW"

