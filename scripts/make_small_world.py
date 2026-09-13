# Week-2 figure (post 2): Watts-Strogatz C(q) and L(q) sweep, sized to match
# the giant component (n=277, k~10), with Marvel's real clustering and path
# length drawn in as reference lines.
import json
import matplotlib.pyplot as plt

BG, PANEL = "#0b0b0d", "#111013"
LINE, MARVEL = "#4C72B0", "#e8434b"
TEXT, MUTED, GRID = "#e9e6df", "#9a9ea5", "#33333a"

with open("../assets/data/week2-analysis.json", encoding="utf-8") as f:
    d = json.load(f)

ws = d["watts_strogatz"]
qs = ws["q"]

plt.rcParams["font.family"] = "monospace"
fig, axes = plt.subplots(1, 2, figsize=(11.5, 5), facecolor=BG)

def style(ax, title, ylabel):
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.set_xscale("symlog", linthresh=0.001)
    ax.set_xlabel("rewiring probability q", color=MUTED, fontsize=11.5)
    ax.set_ylabel(ylabel, color=MUTED, fontsize=12)
    ax.set_title(title, color=TEXT, fontsize=14, pad=10)
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.grid(True, color=GRID, linewidth=0.5, alpha=0.5)

style(axes[0], "Clustering C(q)", "C(q)")
axes[0].errorbar(qs, ws["C_mean"], yerr=ws["C_std"], fmt="o-", color=LINE, capsize=3)
axes[0].axhline(ws["marvel_C"], color=MARVEL, ls="--", lw=1.8, label=f"Marvel C ≈ {ws['marvel_C']:.2f}")
axes[0].legend(facecolor=PANEL, edgecolor=GRID, fontsize=10, labelcolor=TEXT)

style(axes[1], "Mean shortest path L(q)", "L(q)")
axes[1].errorbar(qs, ws["L_mean"], yerr=ws["L_std"], fmt="o-", color=LINE, capsize=3)
axes[1].axhline(ws["marvel_L"], color=MARVEL, ls="--", lw=1.8, label=f"Marvel L ≈ {ws['marvel_L']:.2f}")
axes[1].legend(facecolor=PANEL, edgecolor=GRID, fontsize=10, labelcolor=TEXT)

fig.suptitle(f"Watts–Strogatz sweep (n={ws['n']}, k={ws['k']}) vs. the real Marvel giant component",
             color=TEXT, fontsize=14.5, y=1.03)
plt.tight_layout()
plt.savefig("../assets/img/small-world.png", dpi=190, facecolor=BG, bbox_inches="tight")
print("saved small-world.png")
