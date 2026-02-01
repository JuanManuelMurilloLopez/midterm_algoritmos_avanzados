import heapq


def dijkstra_explain(graph, start_team, target_team):
    priority_queue = [(0.0, start_team)]

    distance_from_start = {start_team: 0.0}

    previous_team = {}

    visited_teams = []

    relaxations_log = []

    while priority_queue:
        current_cost, current_team = heapq.heappop(priority_queue)

        if current_team in visited_teams:
            continue

        visited_teams.append(current_team)

        if current_team == target_team:
            break

        for edge in graph.adj.get(current_team, []):
            neighbor_team = edge.to
            edge_cost = edge.weight
            new_cost = current_cost + edge_cost

            if (
                neighbor_team not in distance_from_start
                or new_cost < distance_from_start[neighbor_team]
            ):
                relaxations_log.append({
                    "from_team": current_team,
                    "to_team": neighbor_team,
                    "previous_cost": distance_from_start.get(neighbor_team),
                    "new_cost": new_cost,
                    "match_result": edge.meta["result"],
                    "edge_cost": edge_cost
                })

                distance_from_start[neighbor_team] = new_cost
                previous_team[neighbor_team] = current_team
                heapq.heappush(priority_queue, (new_cost, neighbor_team))

    if target_team not in distance_from_start:
        return None, [], {
            "reachable": False,
            "visited_teams": visited_teams,
            "relaxations": relaxations_log
        }

    optimal_path = [target_team]
    while optimal_path[-1] != start_team:
        optimal_path.append(previous_team[optimal_path[-1]])
    optimal_path.reverse()

    return distance_from_start[target_team], optimal_path, {
        "reachable": True,
        "optimal_path": optimal_path,
        "total_cost": distance_from_start[target_team],
        "visited_teams": visited_teams,
        "relaxations": relaxations_log
    }
