# Week-2 figure: Erdos-Renyi giant-component phase transition at n=303,
# with Marvel's real mean degree marked to show it sits deep in the
# "connected" regime -- so the giant component itself is unremarkable;
# the surprise is elsewhere (the isolates/island), covered in the post text.
import json
import numpy as np
import matplotlib.pyplot as plt

BG, PANEL = "#0b0b0d", "#111013"
LINE, MARVEL = "#4C72B0", "#e8434b"
TEXT, MUTED, GRID = "#e9e6df", "#9a9ea5", "#33333a"

with open("../assets/data/week2-analysis.json", encoding="utf-8") as f:
    d = json.load(f)

pt = d["phase_transition"]
k_grid = np.array(pt["k_grid"]); mean = np.array(pt["mean"]); std = np.array(pt["std"])
marvel_k = pt["marvel_k"]

plt.rcParams["font.family"] = "monospace"
fig, ax = plt.subplots(figsize=(8.5, 5.5), facecolor=BG)
ax.set_facecolor(PANEL)
for spine in ax.spines.values():
    spine.set_color(GRID)

ax.errorbar(k_grid, mean, yerr=std, fmt="o-", color=LINE, capsize=2.5, linewidth=1.3,
            markersize=4, label="G(n,p), n=303 (mean ± std, 20 runs)")
ax.axvline(1.0, color=MUTED, ls="--", lw=1.2, alpha=0.8, label="critical point ⟨k⟩ = 1")
ax.axvline(marvel_k, color=MARVEL, ls="--", lw=1.6, label=f"Marvel's real ⟨k⟩ ≈ {marvel_k:.1f}")

ax.set_xlabel("average degree ⟨k⟩", color=MUTED, fontsize=12)
ax.set_ylabel("giant component size / n", color=MUTED, fontsize=12)
ax.set_title("The giant-component phase transition (n=303)", color=TEXT, fontsize=15, pad=14)
ax.tick_params(colors=MUTED, labelsize=10.5, length=4)
ax.grid(True, color=GRID, linewidth=0.5, alpha=0.6)
ax.legend(facecolor=PANEL, edgecolor=GRID, fontsize=10.5, labelcolor=TEXT, loc="lower right")

plt.tight_layout()
plt.savefig("../assets/img/phase-transition.png", dpi=190, facecolor=BG, bbox_inches="tight")
print("saved phase-transition.png")
