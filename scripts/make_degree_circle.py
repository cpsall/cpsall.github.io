# Builds the week-1 hero figure: a circular layout with nodes ordered by
# degree (lowest -> highest), which is the layout chosen in the post after
# comparing it against force-directed, alphabetical-circular and random
# layouts. See posts/week1-the-unlinked.html for the justification.
#
# The analysis itself (who's alone, who's on the island, who's the hub) is
# NOT recomputed here -- it's read from assets/data/week1-analysis.json,
# written by analyze_alone.py. Run that script first if the json is missing
# or the source TSVs have changed.

import json
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

BG = "#0b0b0d"
GIANT = "#5b6b7a"
ISLAND = "#d9a441"
ISOLATE = "#c81d25"
HUB = "#f2f0ea"
EDGE = "#2a2f36"
TEXT = "#e9e6df"
MUTED = "#8b8f96"

nodes = pd.read_csv("../../week1_nodes.tsv", sep="\t", comment="#", quoting=3)
edges = pd.read_csv("../../week1_edges.tsv", sep="\t", comment="#", names=["source", "target"])
id_to_name = dict(zip(nodes.node_id, nodes.name))

with open("../assets/data/week1-analysis.json", encoding="utf-8") as f:
    analysis = json.load(f)

island = set(analysis["island"]["members"])
isolates = set(item["id"] for item in analysis["isolates"])
deg = analysis["degree"]
hub_from_analysis = analysis["hub"]["id"]

# Edges still have to come from the raw TSVs -- the analysis json stores
# membership and degree, not the full edge list, and drawing needs every edge.
G = nx.DiGraph()
G.add_nodes_from(nodes.node_id)
G.add_edges_from(edges.itertuples(index=False))

U = nx.Graph()
U.add_nodes_from(G.nodes)
U.add_edges_from(G.edges)

# Sort nodes by ascending degree. A full nx.circular_layout on this order puts
# the lowest- and highest-degree nodes RIGHT NEXT TO EACH OTHER, because a
# circle wraps (angle 0 and angle 2*pi are the same point) -- that made the
# isolates and the Spider-Man hub collide into one unreadable cluster.
# Spreading the same ordering across a half-circle instead puts "alone" and
# "most linked" at opposite tips, so the ring reads left-to-right as a degree
# axis instead of wrapping back on itself.
degree_order = sorted(U.nodes(), key=lambda n: (deg[n], id_to_name[n]))
G_ordered = nx.Graph()
G_ordered.add_nodes_from(degree_order)
G_ordered.add_edges_from(U.edges())

n = len(degree_order)
pos = {
    node: (np.cos(np.pi * i / (n - 1)), np.sin(np.pi * i / (n - 1)))
    for i, node in enumerate(degree_order)
}

def color_for(n):
    if n in isolates:
        return ISOLATE
    if n in island:
        return ISLAND
    return GIANT

colors = [color_for(n) for n in G_ordered.nodes()]
sizes = [22 + deg[n] * 3.6 for n in G_ordered.nodes()]

fig, ax = plt.subplots(figsize=(13, 8.5), facecolor=BG)
ax.set_facecolor(BG)

nx.draw_networkx_edges(G_ordered, pos, ax=ax, edge_color=EDGE, width=0.35, alpha=0.3)
nx.draw_networkx_nodes(G_ordered, pos, ax=ax, node_size=sizes, node_color=colors, linewidths=0)

hub = hub_from_analysis
hx, hy = pos[hub]
ax.scatter([hx], [hy], s=deg[hub] * 3.6 + 22, color=HUB, zorder=5)
ax.annotate(id_to_name[hub], (hx, hy), xytext=(hx, hy + 0.1),
            color=TEXT, fontsize=13, fontweight="bold", ha="center",
            path_effects=[pe.withStroke(linewidth=3, foreground=BG)])

# The isolates famous for reasons the graph can't see -- ringed in white so
# they stand out from the other red dots bunched at the same tip. Flagged in
# the analysis step, not hardcoded here.
highlight = [item["id"] for item in analysis["isolates"] if item["famous_despite_isolation"]]
for nid in highlight:
    x, y = pos[nid]
    ax.scatter([x], [y], s=90, facecolors="none", edgecolors=HUB, linewidths=1.3, zorder=6)

# Callouts live in the empty lower half of the canvas -- the arc itself only
# occupies y >= 0, so there's a clean strip below it for labels.
iso_tip = pos[degree_order[0]]
ax.annotate(
    "ALONE — degree 0\n" + "\n".join(id_to_name[nid] for nid in highlight),
    xy=iso_tip, xytext=(iso_tip[0] - 0.05, -0.55),
    color=ISOLATE, fontsize=11, fontweight="bold", ha="center", fontfamily="monospace",
    arrowprops=dict(arrowstyle="-", color=ISOLATE, lw=0.8, alpha=0.7),
)
ax.annotate(
    f"MOST LINKED — degree {deg[hub]}\n{id_to_name[hub]}",
    xy=(hx, hy), xytext=(hx + 0.05, -0.35),
    color=MUTED, fontsize=11, fontweight="bold", ha="center", fontfamily="monospace",
    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, alpha=0.7),
)

ax.text(0, 1.18, "303 characters, one arc, sorted low degree -> high degree", color=MUTED,
        fontsize=13, ha="center", fontfamily="monospace")

legend_items = [
    (GIANT, f"giant component ({analysis['giant_component']['size']})"),
    (ISLAND, f"Strikeforce: Morituri island ({analysis['island']['size']})"),
    (ISOLATE, f"alone ({len(analysis['isolates'])})"),
]
for i, (c, label) in enumerate(legend_items):
    ly = -0.62 - i * 0.09
    ax.scatter([-1.28], [ly], s=45, color=c)
    ax.text(-1.2, ly, label, color=MUTED, fontsize=10, va="center", fontfamily="monospace")

ax.set_xlim(-1.35, 1.35)
ax.set_ylim(-0.95, 1.3)
ax.set_aspect("equal")
ax.axis("off")

plt.tight_layout()
plt.savefig("../assets/img/degree-circle.png", dpi=170, facecolor=BG, bbox_inches="tight")
print("saved")
