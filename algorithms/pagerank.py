def calculate_pagerank(graph, damping=0.85, iterations=50):
    nodes = set(graph.adj.keys())
    for neighbors in graph.adj.values():
        for edge in neighbors:
            nodes.add(edge["to"])
    
    num_nodes = len(nodes)
    if num_nodes == 0:
        return {}, {}

    pagerank = {node: 1.0 for node in nodes}
    
    for _ in range(iterations):
        new_pagerank = {node: (1 - damping) for node in nodes}
        
        for node in nodes:
            outgoing_edges = graph.adj.get(node, [])
            if not outgoing_edges:
                continue
            share_score = pagerank[node] * damping / len(outgoing_edges)
            
            for edge in outgoing_edges:
                target = edge["to"]
                new_pagerank[target] += share_score
        
        pagerank = new_pagerank

    sorted_ranks = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
    explanation = {
        "algorithm": "PageRank (Team Prestige)",
        "top_3": sorted_ranks[:3],
        "damping_factor": damping
    }

    return pagerank, explanation