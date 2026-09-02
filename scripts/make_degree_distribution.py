# Builds the week-1 degree-distribution figure: in-degree vs out-degree,
# on linear and log-log axes side by side. Reads assets/data/week1-analysis.json
# (written by analyze_alone.py) for the in_degree / out_degree dictionaries --
# no recomputation here, just plotting.

import json
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

BG = "#0b0b0d"
PANEL = "#111013"
IN_COLOR = "#e8434b"
OUT_COLOR = "#e8b84b"
TEXT = "#e9e6df"
MUTED = "#9a9ea5"
GRID = "#33333a"

with open("../assets/data/week1-analysis.json", encoding="utf-8") as f:
    analysis = json.load(f)

in_deg = np.array(list(analysis["in_degree"].values()))
out_deg = np.array(list(analysis["out_degree"].values()))
n = len(in_deg)

def distribution(values):
    # P(k+1): shift by 1 so degree-0 nodes (the isolates) still have a
    # positive x-value and survive on a log axis instead of vanishing at 0.
    counts = Counter(values + 1)
    ks = np.array(sorted(counts))
    ps = np.array([counts[k] / n for k in ks])
    return ks, ps

in_k, in_p = distribution(in_deg)
out_k, out_p = distribution(out_deg)

plt.rcParams["font.family"] = "monospace"

fig, axes = plt.subplots(1, 2, figsize=(15, 7), facecolor=BG)

def style_axis(ax, title):
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=11, length=4)
    ax.set_xlabel("k + 1", color=MUTED, fontsize=12)
    ax.set_ylabel("P(k + 1)", color=MUTED, fontsize=12)
    ax.set_title(title, color=TEXT, fontsize=15, pad=14)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=0.7)

def plot_series(ax, k, p, color, marker, label):
    ax.plot(k, p, color=color, linewidth=1.1, alpha=0.55, zorder=2)
    ax.scatter(k, p, s=64, color=color, marker=marker, label=label,
               edgecolors=BG, linewidths=1.1, zorder=3)

style_axis(axes[0], "linear")
plot_series(axes[0], in_k, in_p, IN_COLOR, "o", "in-degree")
plot_series(axes[0], out_k, out_p, OUT_COLOR, "^", "out-degree")

style_axis(axes[1], "log-log")
plot_series(axes[1], in_k, in_p, IN_COLOR, "o", "in-degree")
plot_series(axes[1], out_k, out_p, OUT_COLOR, "^", "out-degree")
axes[1].set_xscale("log")
axes[1].set_yscale("log")

for ax in axes:
    ax.legend(facecolor=PANEL, edgecolor=GRID, fontsize=11.5, labelcolor=TEXT,
               markerscale=1.2, loc="upper right")

fig.suptitle("In-degree vs. out-degree distribution", color=TEXT, fontsize=17, y=1.03)

plt.tight_layout()
plt.savefig("../assets/img/degree-distribution.png", dpi=200, facecolor=BG, bbox_inches="tight")
print("saved")
