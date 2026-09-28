import json
import networkx as nx
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

nodes = pd.read_csv(BASE_DIR / "../../week1_nodes.tsv", sep="\t", comment="#", quoting=3)
edges = pd.read_csv(BASE_DIR / "../../week1_edges.tsv", sep="\t", comment="#", names=["source", "target"])
id_to_name = dict(zip(nodes.node_id, nodes.name))
id_to_desc = dict(zip(nodes.node_id, nodes.description))

G = nx.DiGraph()
G.add_nodes_from(nodes.node_id)
G.add_edges_from(edges.itertuples(index=False))

# Undirected Graph
U = nx.Graph()
U.add_nodes_from(G.nodes)
U.add_edges_from(G.edges)

print("Analyzing maximal cliques...")
all_cliques = list(nx.find_cliques(U))

# Choose a character by node id (or name) to inspect
# Example: "Hercules" is a valid node id in the Marvel data set.
target_character = "Hercules_(Marvel_Comics)"

# Keep only maximal cliques that include the selected character
character_cliques = [
    sorted(clique)
    for clique in all_cliques
    if target_character in clique
]

if character_cliques:
    top_size = max(len(c) for c in character_cliques)
    top_size_cliques = [
        [id_to_name.get(node, str(node)) for node in clique]
        for clique in character_cliques
        if len(clique) == top_size
    ]

    print(f"Largest clique size among cliques containing {target_character}: {top_size}")
    for clique in top_size_cliques:
        print(clique)
else:
    print(f"No maximal clique contains {target_character}.")

# Print all direct neighbors of the selected character, one below the other.
if target_character in U:
    neighbors = sorted(U.neighbors(target_character))
    print(f"\nNeighbors of {target_character} ({len(neighbors)}):")
    for neighbor in neighbors:
        print(f"- {id_to_name.get(neighbor, str(neighbor))}")
else:
    print(f"\nCharacter not found: {target_character}")


import networkx as nx


# ============================================================
# Helper function: print graph statistics
# ============================================================

def print_graph_stats(G, title="Graph"):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    # Basic
    print(f"Nodes:                    {G.number_of_nodes():,}")
    print(f"Edges:                    {G.number_of_edges():,}")

    # --------------------------------------------------------
    # Connected components
    # For a directed graph, weak connectivity ignores edge
    # direction and tells us whether nodes belong to the same
    # underlying network.
    # --------------------------------------------------------

    components = list(nx.weakly_connected_components(G))

    print(f"Connected components:     {len(components):,}")

    # Largest / giant component
    giant = max(components, key=len)

    print(f"Giant component size:     {len(giant):,}")
    print(
        f"Giant component fraction: "
        f"{len(giant) / G.number_of_nodes():.2%}"
    )

    # --------------------------------------------------------
    # Shortest paths
    # Calculate these on the giant component.
    #
    # For a directed graph, nx.average_shortest_path_length()
    # respects edge direction.
    # --------------------------------------------------------

    giant_G = G.subgraph(giant).copy()

    if nx.is_strongly_connected(giant_G):
        avg_path = nx.average_shortest_path_length(giant_G)
        diameter = nx.diameter(giant_G)

        print(f"Average shortest path:   {avg_path:.4f}")
        print(f"Diameter:                 {diameter:,}")

    else:
        # Weakly connected does not guarantee directed paths
        # in both directions.
        print("Average shortest path:   N/A (not strongly connected)")
        print("Diameter:                 N/A (not strongly connected)")

        # Weak-distance version is still useful for the network's
        # underlying structure.
        giant_undirected = giant_G.to_undirected()

        avg_path_weak = nx.average_shortest_path_length(
            giant_undirected
        )
        diameter_weak = nx.diameter(giant_undirected)

        print(f"Avg shortest path (weak): {avg_path_weak:.4f}")
        print(f"Diameter (weak):          {diameter_weak:,}")

    # --------------------------------------------------------
    # Density
    # --------------------------------------------------------

    print(f"Density:                  {nx.density(G):.6f}")

    # --------------------------------------------------------
    # Degree statistics
    # --------------------------------------------------------

    in_degrees = dict(G.in_degree())
    out_degrees = dict(G.out_degree())

    avg_in = sum(in_degrees.values()) / len(in_degrees)
    avg_out = sum(out_degrees.values()) / len(out_degrees)

    print(f"Average in-degree:        {avg_in:.4f}")
    print(f"Average out-degree:       {avg_out:.4f}")

    print(
        f"Maximum in-degree:        "
        f"{max(in_degrees.values()):,}"
    )

    print(
        f"Maximum out-degree:       "
        f"{max(out_degrees.values()):,}"
    )


# ============================================================
# ORIGINAL GRAPH
# ============================================================

print_graph_stats(G, "ORIGINAL GRAPH")


# ============================================================
# TOP 6 BETWEENNESS NODES
# ============================================================

betweenness = nx.betweenness_centrality(G)

top_6 = sorted(
    betweenness.items(),
    key=lambda x: x[1],
    reverse=True
)[:6]


print("\n" + "=" * 70)
print("TOP 6 BETWEENNESS NODES")
print("=" * 70)

for rank, (node, score) in enumerate(top_6, start=1):
    print(f"{rank}. {node}  ({score:.6f})")


# ============================================================
# REMOVE EACH TOP NODE INDIVIDUALLY
# ============================================================

for rank, (node, score) in enumerate(top_6, start=1):

    # Copy ORIGINAL graph each time.
    # This means we measure the effect of removing this node
    # independently rather than accumulating removals.
    G_removed = G.copy()
    G_removed.remove_node(node)

    print_graph_stats(
        G_removed,
        f"REMOVE #{rank}: {node} "
        f"(betweenness = {score:.6f})"
    )


