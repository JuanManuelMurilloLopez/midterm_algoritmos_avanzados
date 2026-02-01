from .models.TeamGraph import TeamGraph
from .algorithms.dijkstra import dijkstra_explain

graph = TeamGraph()

graph.add_match("TeamA", "TeamB", "G")  
graph.add_match("TeamB", "TeamC", "E")  
graph.add_match("TeamA", "TeamC", "P")  
graph.add_match("TeamC", "TeamD", "G")  
graph.add_match("TeamB", "TeamD", "P")  

cost, path, explanation = dijkstra_explain(
    graph,
    start_team="TeamA",
    target_team="TeamD"
)

print("=== RESULTADO ===")
print("Costo total:", cost)
print("Camino óptimo:", path)

print("\n=== EXPLICACIÓN ===")
print("Equipos visitados:", explanation["visited_teams"])

print("\nRelajaciones:")
for r in explanation["relaxations"]:
    print(
        f"{r['from_team']} -> {r['to_team']} | "
        f"resultado={r['match_result']} | "
        f"costo_arista={r['edge_cost']} | "
        f"nuevo_costo={r['new_cost']}"
    )
