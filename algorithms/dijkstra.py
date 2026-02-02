import heapq


def dijkstra_explain(graph, start, target):
    pq = [(0.0, start)]
    dist = {start: 0.0}
    prev = {}
    explanation = []

    while pq:
        cost, node = heapq.heappop(pq)

        if node == target:
            break

        for edge in graph.adj.get(node, []):
            next_node = edge["to"]
            weight = edge["weight"]
            new_cost = cost + weight

            if next_node not in dist or new_cost < dist[next_node]:
                dist[next_node] = new_cost
                prev[next_node] = node
                heapq.heappush(pq, (new_cost, next_node))

                explanation.append({
                    "from": node,
                    "to": next_node,
                    "edge_cost": weight,
                    "total_cost": new_cost,
                    "reason": f"ritmo del rival = {edge['meta']['rhythm']:.2f}"
                })

    path = []
    cur = target
    while cur in prev:
        path.append(cur)
        cur = prev[cur]
    path.append(start)
    path.reverse()

    return dist.get(target, float("inf")), path, explanation
