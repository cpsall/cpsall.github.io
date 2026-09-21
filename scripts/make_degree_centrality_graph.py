import json
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

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
with open(BASE_DIR / "../assets/data/week3-analysis.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Handles both "nodes" and "node_metrics" schema keys gracefully
nodes_data = data.get("nodes", data.get("node_metrics", []))
df = pd.DataFrame(nodes_data)

# Flexible column mapping for compatibility
deg_col = "degree" if "degree" in df.columns else "degree_undirected"
bet_col = "betweenness" if "betweenness" in df.columns else "betweenness_centrality"
cls_col = "closeness" if "closeness" in df.columns else "closeness_centrality"

# 2. Setup Figure Styling
fig, ax = plt.subplots(figsize=(8.5, 6.5), facecolor=BG, dpi=190)
ax.set_facecolor(PANEL)
for spine in ax.spines.values():
    spine.set_color(GRID)

# 3. Scatter Plot (x=Degree, y=Betweenness, color=Closeness)
scatter = ax.scatter(
    df[deg_col],
    df[bet_col],
    c=df[cls_col],
    cmap="magma",
    alpha=0.85,
    s=45,
    edgecolors="none",
    zorder=4,
)

ax.set_xscale("log")

# Add & style Colorbar for 3rd metric
cbar = fig.colorbar(scatter, ax=ax)
cbar.set_label("Closeness Centrality", fontsize=11, color=MUTED, labelpad=10)
cbar.ax.yaxis.set_tick_params(color=MUTED, labelsize=9.5)
plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color=MUTED)
cbar.outline.set_edgecolor(GRID)

# Ticks & Grid
ax.tick_params(colors=MUTED, labelsize=10.5, length=4)
ax.grid(True, color=GRID, linewidth=0.5, alpha=0.6)

# Labels and Title
ax.set_xlabel("Degree k (log scale)", color=MUTED, fontsize=11.5)
ax.set_ylabel("Normalized Betweenness Centrality", color=MUTED, fontsize=11.5)
ax.set_title("Degree vs. Betweenness Centrality", color=TEXT, fontsize=14, pad=14)

# 4. Pick High-Interest Nodes to Annotate
top_betweenness = df.nlargest(6, bet_col)
top_degree = df.nlargest(6, deg_col)

# High-ratio outliers: High Betweenness relative to low Degree (Key Bridges)
df["ratio"] = df[bet_col] / (df[deg_col] + 1)
top_bridges = df.nlargest(4, "ratio")

annotated = pd.concat([top_betweenness, top_degree, top_bridges]).drop_duplicates(
    subset=["node_id"] if "node_id" in df.columns else ["name"]
)

# 5. Annotate Nodes
texts = []
for _, row in annotated.iterrows():
    name = row["name"]
    x = row[deg_col]
    y = row[bet_col]

    if HAS_ADJUST_TEXT:
        texts.append(
            ax.text(x, y, name, color=TEXT, fontsize=8, fontweight="medium")
        )
    else:
        ax.annotate(
            name,
            xy=(x, y),
            xytext=(6, 6),
            textcoords="offset points",
            color=TEXT,
            fontsize=8,
            fontweight="medium",
            bbox=dict(boxstyle="round,pad=0.2", fc=PANEL, ec=GRID, alpha=0.85),
            arrowprops=dict(
                arrowstyle="->", connectionstyle="arc3,rad=0", color=MUTED, lw=0.5
            ),
        )

# Untangle labels automatically if adjustText is available
if HAS_ADJUST_TEXT:
    adjust_text(
        texts,
        ax=ax,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.5, alpha=0.8),
    )

# 6. Save & Display
plt.tight_layout()
out_path = BASE_DIR / "../assets/img/degree-vs-betweenness.png"
plt.savefig(out_path, dpi=190, facecolor=BG, bbox_inches="tight")
plt.show()

print(f"saved {out_path}")