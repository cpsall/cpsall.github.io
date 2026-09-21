from collections import Counter
import json
import os
import networkx as nx
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
# -----------------------------------------------------------------------------
# 1. Load Data & Build Graphs
# -----------------------------------------------------------------------------
nodes = pd.read_csv(BASE_DIR / "../../week1_nodes.tsv", sep="\t", comment="#", quoting=3)
edges = pd.read_csv(
    BASE_DIR / "../../week1_edges.tsv", sep="\t", comment="#", names=["source", "target"]
)

# Build mappings with fallbacks for missing descriptions
id_to_name = dict(zip(nodes.node_id, nodes.name))
id_to_desc = dict(
    zip(
        nodes.node_id,
        nodes.description.fillna("No description available."),
    )
)

# Directed Graph
G = nx.DiGraph()
G.add_nodes_from(nodes.node_id)
G.add_edges_from(edges.itertuples(index=False))

# Undirected Graph
U = nx.Graph()
U.add_nodes_from(G.nodes)
U.add_edges_from(G.edges)

num_nodes = U.number_of_nodes()
print(
    f"Loaded graph with {num_nodes} nodes and {U.number_of_edges()} undirected edges."
)

# -----------------------------------------------------------------------------
# 2. Path Lengths & Giant Connected Component (GCC)
# -----------------------------------------------------------------------------
# Path metrics like average shortest path and diameter require a connected graph.
is_connected = nx.is_connected(U)
connected_components = list(nx.connected_components(U))
num_components = len(connected_components)

gcc_nodes = max(connected_components, key=len)
gcc = U.subgraph(gcc_nodes).copy()
gcc_size = gcc.number_of_nodes()

print("Calculating shortest path metrics...")
if is_connected:
    avg_shortest_path = nx.average_shortest_path_length(U)
    diameter = nx.diameter(U)
else:
    print(
        f"Graph is disconnected ({num_components} components). "
        f"Computing path metrics on the Giant Connected Component ({gcc_size}/{num_nodes} nodes)."
    )
    avg_shortest_path = nx.average_shortest_path_length(gcc)
    diameter = nx.diameter(gcc)

# -----------------------------------------------------------------------------
# 3. Compute Node Centralities & Metrics
# -----------------------------------------------------------------------------
print("Calculating node centralities...")

# Degrees
in_degrees = dict(G.in_degree())
out_degrees = dict(G.out_degree())
total_directed_degrees = dict(G.degree())
undirected_degrees = dict(U.degree())

# Normalized Betweenness Centrality
betweenness = nx.betweenness_centrality(G, normalized=True)
top_betweenness = sorted(
    betweenness.items(), key=lambda item: item[1], reverse=True
)[:10]
print(top_betweenness)

# Closeness Centrality (NetworkX normalizes by component size)
closeness = nx.closeness_centrality(U)

# Harmonic Centrality (Divide by N - 1 to normalize to [0, 1])
raw_harmonic = nx.harmonic_centrality(U)
harmonic = {
    node: score / (num_nodes - 1) if num_nodes > 1 else 0.0
    for node, score in raw_harmonic.items()
}

# Eigenvector Centrality
try:
    eigenvector = nx.eigenvector_centrality(U, max_iter=2000)
except nx.PowerIterationFailedConvergence:
    print("Eigenvector centrality power iteration failed; falling back to numpy solver.")
    eigenvector = nx.eigenvector_centrality_numpy(U)

# PageRank (Useful directed metric)
pagerank = nx.pagerank(G)

# Clustering Coefficient
clustering = nx.clustering(U)

# -----------------------------------------------------------------------------
# 4. Compute Edge Betweenness
# -----------------------------------------------------------------------------
print("Calculating edge betweenness centrality...")
edge_betweenness_dict = nx.edge_betweenness_centrality(U, normalized=True)

edge_betweenness_list = [
    {
        "source": str(u),
        "target": str(v),
        "source_name": id_to_name.get(u, str(u)),
        "target_name": id_to_name.get(v, str(v)),
        "betweenness": round(score, 6),
    }
    for (u, v), score in sorted(
        edge_betweenness_dict.items(), key=lambda x: x[1], reverse=True
    )
]

for i in range(0,10):
    edge_info = edge_betweenness_list[i]
    print(
        f"Edge {i+1}: {edge_info['source_name']}  "
        f"<-> {edge_info['target_name']} , "
        f"Betweenness: {edge_info['betweenness']}"
    )

# -----------------------------------------------------------------------------
# 5. Maximal Cliques Analysis
# -----------------------------------------------------------------------------
print("Analyzing maximal cliques...")
all_cliques = list(nx.find_cliques(U))

# Count cliques by size
clique_sizes = Counter(len(c) for c in all_cliques)
clique_counts_by_size = {
    str(size): count for size, count in sorted(clique_sizes.items())
}

# Top 10 largest cliques
sorted_cliques = sorted(all_cliques, key=len, reverse=True)
top_10_cliques = [
    {
        "size": len(clique),
        "node_ids": [str(node) for node in clique],
        "node_names": [id_to_name.get(node, str(node)) for node in clique],
    }
    for clique in sorted_cliques[:10]
]

# -----------------------------------------------------------------------------
# 6. Assemble Node Objects
# -----------------------------------------------------------------------------
nodes_report = []
for node_id in nodes.node_id:
    nodes_report.append(
        {
            "node_id": str(node_id),
            "name": id_to_name.get(node_id, str(node_id)),
            "description": id_to_desc.get(node_id, ""),
            # Degree Metrics
            "in_degree": in_degrees.get(node_id, 0),
            "out_degree": out_degrees.get(node_id, 0),
            "total_directed_degree": total_directed_degrees.get(node_id, 0),
            "degree": undirected_degrees.get(node_id, 0),
            # Centrality Metrics (Normalized)
            "betweenness": round(betweenness.get(node_id, 0.0), 6),
            "closeness": round(closeness.get(node_id, 0.0), 6),
            "harmonic": round(harmonic.get(node_id, 0.0), 6),
            "eigenvector": round(eigenvector.get(node_id, 0.0), 6),
            "pagerank": round(pagerank.get(node_id, 0.0), 6),
            # Local Subgraph Metrics
            "clustering_coefficient": round(clustering.get(node_id, 0.0), 6),
            "is_in_gcc": node_id in gcc_nodes,
        }
    )

# -----------------------------------------------------------------------------
# 7. Final Payload Structure & Export
# -----------------------------------------------------------------------------
report = {
    "summary": {
        "total_nodes": num_nodes,
        "total_directed_edges": G.number_of_edges(),
        "total_undirected_edges": U.number_of_edges(),
        "is_connected": is_connected,
        "num_connected_components": num_components,
        "gcc_node_count": gcc_size,
        "gcc_fraction": round(gcc_size / num_nodes, 4),
        "average_shortest_path_length": round(avg_shortest_path, 4),
        "diameter": diameter,
        "path_metrics_scope": "entire_graph"
        if is_connected
        else "giant_connected_component",
    },
    "clique_analysis": {
        "total_maximal_cliques": len(all_cliques),
        "maximal_cliques_by_size": clique_counts_by_size,
        "top_10_biggest_cliques": top_10_cliques,
    },
    "edge_betweenness": edge_betweenness_list,
    "nodes": nodes_report,
}

output_dir = BASE_DIR / "../assets/data"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "week3-analysis.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\nSuccessfully wrote analysis report to {output_path}")