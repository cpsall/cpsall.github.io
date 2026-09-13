# Week-2 figure: Marvel's degree CCDF vs. a matched Erdos-Renyi network and a
# matched Barabasi-Albert network. Reads week2-analysis.json (written by
# analyze_week2.py) -- no recomputation here, just plotting.
import json
import matplotlib.pyplot as plt

BG, PANEL = "#0b0b0d", "#111013"
MARVEL, ER, BA = "#e8434b", "#9a9ea5", "#d9a441"
TEXT, MUTED, GRID = "#e9e6df", "#9a9ea5", "#33333a"

with open("../assets/data/week2-analysis.json", encoding="utf-8") as f:
    d = json.load(f)

dd = d["degree_distribution"]
fig, ax = plt.subplots(figsize=(8.5, 6.5), facecolor=BG)
ax.set_facecolor(PANEL)
for spine in ax.spines.values():
    spine.set_color(GRID)
plt.rcParams["font.family"] = "monospace"

ax.loglog(dd["er"]["k"], dd["er"]["p"], "-", color=ER, linewidth=1.6, alpha=0.85,
          label=f"Erdős–Rényi, matched n & m")
ax.loglog(dd["ba"]["k"], dd["ba"]["p"], "-", color=BA, linewidth=1.6, alpha=0.9,
          label="Barabási–Albert, matched n & m")
ax.loglog(dd["marvel"]["k"], dd["marvel"]["p"], "o", color=MARVEL, markersize=6,
          markeredgecolor=BG, markeredgewidth=0.8, zorder=5, label="Marvel (real)")

ax.set_xlabel("degree k (log)", color=MUTED, fontsize=12)
ax.set_ylabel("P(K ≥ k) (log)", color=MUTED, fontsize=12)
ax.set_title("Marvel's degree CCDF vs. matched random-graph models", color=TEXT, fontsize=15, pad=14)
ax.tick_params(colors=MUTED, labelsize=10.5, length=4)
ax.grid(True, color=GRID, linewidth=0.5, alpha=0.6)
ax.legend(facecolor=PANEL, edgecolor=GRID, fontsize=11, labelcolor=TEXT, loc="upper right")

plt.tight_layout()
plt.savefig("../assets/img/degree-fit.png", dpi=190, facecolor=BG, bbox_inches="tight")
print("saved degree-fit.png")
