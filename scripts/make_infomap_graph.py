import json
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import networkx as nx

BASE_DIR = Path(__file__).resolve().parent

# -----------------------------------------------------------------------------
# 1. Load Data & Build Graphs
# -----------------------------------------------------------------------------
nodes = pd.read_csv(BASE_DIR / "../../week4_philosophers_nodes.tsv", sep="\t", comment="#", quoting=3)
edges = pd.read_csv(
    BASE_DIR / "../../week4_philosophers_edges.tsv", sep="\t", comment="#", names=["source", "target"]
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

# Option: Install adjustText if you want zero overlapping labels (`pip install adjustText`)
try:
    from adjustText import adjust_text

    HAS_ADJUST_TEXT = True
except ImportError:
    HAS_ADJUST_TEXT = False

# Graphiverse Dark Theme Palette (matching make_degree_fit.py)
BG, PANEL = "#0b0b0d", "#111013"
TEXT, MUTED, GRID = "#e9e6df", "#9a9ea5", "#33333a"

plt.rcParams["font.family"] = "monospace"

# 1. Load analysis JSON
with open(BASE_DIR / "../assets/data/week4-analysis.json", "r", encoding="utf-8") as f:
    data = json.load(f)

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# -------------------------------------------------------------------------
# 4. Infomap communities and node importance
# -------------------------------------------------------------------------

# Get Infomap assignments from the analysis JSON
infomap = data["louvain_vs_infomap"]["infomap_assignments"]

# Assign each graph node to its community
communities = {
    node: infomap[str(node)]
    for node in U.nodes()
    if str(node) in infomap
}

# Keep only nodes with community assignments
G_plot = U.subgraph(communities.keys()).copy()

# Group nodes by community
community_members = {}
for node, community in communities.items():
    community_members.setdefault(community, []).append(node)

# Rank communities by size
ranked_communities = sorted(
    community_members.items(),
    key=lambda item: len(item[1]),
    reverse=True
)

print(f"\nInfomap communities: {len(community_members)}")
print("\nLargest communities:")
for community, members in ranked_communities[:10]:
    print(f"Community {community}: {len(members)} nodes")

# -------------------------------------------------------------------------
# 5. Identify the most important node in each community
# -------------------------------------------------------------------------

# Weighted degree (strength): sum of incident edge weights
#weighted_degree = dict(G_plot.degree(weight="weight"))

weighted_degree = {}
for node, degree in G.degree():
    weighted_degree[node] = degree

# Find the most important node in each community
community_leaders = {}
for community, members in community_members.items():
    leader = max(members, key=lambda node: weighted_degree[node])
    community_leaders[community] = leader

# -------------------------------------------------------------------------
# 6. Layout
# -------------------------------------------------------------------------

# Use an undirected force-directed layout
pos = nx.spring_layout(
    G_plot,
    weight="weight",
    seed=42,
    k=1.5 / np.sqrt(max(G_plot.number_of_nodes(), 1)),
    iterations=200
)

# -------------------------------------------------------------------------
# 7. Colors and sizes
# -------------------------------------------------------------------------

# Assign a distinct color to each community
community_ids = [community for community, _ in ranked_communities]
cmap = plt.get_cmap("turbo", max(len(community_ids), 1))

community_colors = {
    community: cmap(i)
    for i, community in enumerate(community_ids)
}

node_colors = [
    community_colors[communities[node]]
    for node in G_plot.nodes()
]

# Scale node sizes by weighted degree
strengths = np.array(
    [weighted_degree[node] for node in G_plot.nodes()],
    dtype=float
)

if len(strengths) and strengths.max() > 0:
    node_sizes = 25 + 250 * strengths / strengths.max()
else:
    node_sizes = np.full(len(strengths), 25)

# Scale edge widths for visualization
edge_weights = np.array(
    [d["weight"] for _, _, d in G_plot.edges(data=True)],
    dtype=float
)

if len(edge_weights) and edge_weights.max() > 0:
    edge_widths = 0.2 + 1.5 * edge_weights / edge_weights.max()
else:
    edge_widths = np.full(len(edge_weights), 0.2)

# -------------------------------------------------------------------------
# 8. Plot
# -------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(20, 16), facecolor=BG)
ax.set_facecolor(BG)

# Draw edges
nx.draw_networkx_edges(
    G_plot,
    pos,
    ax=ax,
    width=edge_widths,
    edge_color=TEXT,
    alpha=0.12
)

# Draw nodes
nx.draw_networkx_nodes(
    G_plot,
    pos,
    ax=ax,
    node_color=node_colors,
    node_size=node_sizes,
    alpha=0.9,
    linewidths=0.25,
    edgecolors=BG
)

# -------------------------------------------------------------------------
# 9. Label the most important philosopher in the largest communities
# -------------------------------------------------------------------------

TOP_COMMUNITIES_TO_LABEL = 10

labels = {
    community_leaders[community]: str(
        G_plot.nodes[community_leaders[community]].get(
            "name",
            community_leaders[community]
        )
    )
    for community, _ in ranked_communities[:TOP_COMMUNITIES_TO_LABEL]
}

texts = []

for node, label in labels.items():
    x, y = pos[node]

    texts.append(
        ax.text(
            x, y,
            label,
            fontsize=9,
            fontweight="bold",
            color=TEXT,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor=PANEL,
                edgecolor=community_colors[communities[node]],
                linewidth=1.2,
                alpha=0.95
            ),
            zorder=10
        )
    )

# Optionally adjust labels to reduce overlap
if HAS_ADJUST_TEXT and texts:
    adjust_text(
        texts,
        ax=ax,
        arrowprops=dict(
            arrowstyle="-",
            color=MUTED,
            lw=0.6,
            alpha=0.6
        )
    )

# -------------------------------------------------------------------------
# 10. Legend and styling
# -------------------------------------------------------------------------

# Legend for the largest communities
legend_handles = []

for community, members in ranked_communities[:TOP_COMMUNITIES_TO_LABEL]:
    leader = community_leaders[community]
    leader_name = G_plot.nodes[leader].get("name", leader)

    legend_handles.append(
        Line2D(
            [0], [0],
            marker="o",
            color="none",
            markerfacecolor=community_colors[community],
            markeredgecolor="none",
            markersize=9,
            label=f"{leader_name} ({len(members)} nodes)"
        )
    )

ax.legend(
    handles=legend_handles,
    title="Largest Infomap communities",
    loc="upper left",
    facecolor=PANEL,
    edgecolor=GRID,
    labelcolor=TEXT,
    title_fontsize=11,
    fontsize=9
)

ax.set_title(
    "Philosopher Network — Infomap Communities",
    color=TEXT,
    fontsize=19,
    fontweight="bold",
    pad=20
)

ax.text(
    0.99, 0.01,
    f"{G_plot.number_of_nodes()} nodes  |  "
    f"{G_plot.number_of_edges()} edges  |  "
    f"{len(community_members)} communities",
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    color=MUTED,
    fontsize=9
)

ax.axis("off")
plt.tight_layout()
plt.savefig(
    BASE_DIR / "../assets/img/philosopher_communities_infomap.png",
    dpi=300,
    facecolor=BG,
    bbox_inches="tight"
)
plt.show()