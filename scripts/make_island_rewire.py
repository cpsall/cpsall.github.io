# Week-2 figure (post 2): what it takes to merge the 9-member "Strikeforce:
# Morituri" island into the giant component -- adding one outward edge vs.
# rewiring the island's own internal edges outward (which strands members
# instead, since the other endpoint of a rewired edge isn't compensated).
import json
import numpy as np
import matplotlib.pyplot as plt

BG, PANEL = "#0b0b0d", "#111013"
MERGE_COLOR, STRAND_COLOR = "#55a868", "#e8434b"
TEXT, MUTED, GRID = "#e9e6df", "#9a9ea5", "#33333a"

with open("../assets/data/week2-analysis.json", encoding="utf-8") as f:
    d = json.load(f)

curve = d["island_experiments"]["rewire_curve"]
ks = [c["k"] for c in curve]
merge = [c["merge_fraction"] * 100 for c in curve]
stranded = [c["avg_stranded"] for c in curve]

plt.rcParams["font.family"] = "monospace"
fig, ax1 = plt.subplots(figsize=(8.5, 5.5), facecolor=BG)
ax1.set_facecolor(PANEL)
for spine in ax1.spines.values():
    spine.set_color(GRID)

ax1.plot(ks, merge, "o-", color=MERGE_COLOR, linewidth=1.8, markersize=5,
          label="% of trials fully merged into the giant")
ax1.set_xlabel("number of the island's 13 internal edges rewired outward", color=MUTED, fontsize=11.5)
ax1.set_ylabel("merged into the giant (%)", color=MERGE_COLOR, fontsize=12)
ax1.tick_params(axis="y", colors=MERGE_COLOR, labelsize=10.5)
ax1.tick_params(axis="x", colors=MUTED, labelsize=10.5)
ax1.grid(True, color=GRID, linewidth=0.5, alpha=0.5)

ax2 = ax1.twinx()
ax2.plot(ks, stranded, "s--", color=STRAND_COLOR, linewidth=1.6, markersize=5,
          label="avg. island members stranded at degree 0")
ax2.set_ylabel("members stranded (of 9)", color=STRAND_COLOR, fontsize=12)
ax2.tick_params(axis="y", colors=STRAND_COLOR, labelsize=10.5)
for spine in ax2.spines.values():
    spine.set_visible(False)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, facecolor=PANEL, edgecolor=GRID,
           fontsize=9.8, labelcolor=TEXT, loc="upper center")

fig.suptitle("Redirecting the island's own links outward: helps, then hurts", color=TEXT, fontsize=14.5, y=1.01)
plt.tight_layout()
plt.savefig("../assets/img/island-rewire.png", dpi=190, facecolor=BG, bbox_inches="tight")
print("saved island-rewire.png")
