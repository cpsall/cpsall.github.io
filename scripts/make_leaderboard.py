# Builds the "who's linked to most vs. who links out most" leaderboard figure
# -- two horizontal bar charts side by side, reading top_in_degree /
# top_out_degree straight from assets/data/week1-analysis.json.

import json
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

top_in = analysis["top_in_degree"]
top_out = analysis["top_out_degree"]

plt.rcParams["font.family"] = "monospace"

fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor=BG)

def bar_panel(ax, rows, color, title):
    names = [r["name"] for r in rows][::-1]
    values = [r["degree"] for r in rows][::-1]
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_visible(False)
    bars = ax.barh(names, values, color=color, height=0.6, zorder=3)
    ax.set_xlim(0, max(values) * 1.28)
    ax.tick_params(colors=TEXT, labelsize=13, length=0)
    ax.xaxis.set_visible(False)
    ax.set_title(title, color=TEXT, fontsize=14, pad=12, loc="left")
    for bar, v in zip(bars, values):
        ax.text(bar.get_width() + max(values) * 0.03, bar.get_y() + bar.get_height() / 2,
                str(v), color=color, fontsize=13, va="center", fontweight="bold")

bar_panel(axes[0], top_in, IN_COLOR, "highest IN-degree — most linked TO")
bar_panel(axes[1], top_out, OUT_COLOR, "highest OUT-degree — links out the most")

fig.suptitle("Two different top fives", color=TEXT, fontsize=17, y=1.05)
fig.text(0.5, 0.985, "no character appears on both lists", color=MUTED,
          fontsize=11.5, ha="center")

plt.tight_layout()
plt.savefig("../assets/img/leaderboard.png", dpi=200, facecolor=BG, bbox_inches="tight")
print("saved")
