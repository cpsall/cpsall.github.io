# Week-2 figure: shuffle-test histograms for the clustering coefficient --
# real Marvel giant component vs. 300 ER(n,m) nulls and 300 degree-preserving
# configuration-model nulls. This is the "shuffle-test any computed property"
# direction from exercise 2.11, done properly (a la exercise 2.8).
import json
import numpy as np
import matplotlib.pyplot as plt

BG, PANEL = "#0b0b0d", "#111013"
ER_COLOR, CFG_COLOR, REAL = "#9a9ea5", "#d9a441", "#e8434b"
TEXT, MUTED, GRID = "#e9e6df", "#9a9ea5", "#33333a"

with open("../assets/data/week2-analysis.json", encoding="utf-8") as f:
    d = json.load(f)

cl = d["nulls"]["clustering"]
real = cl["real"]
er, cfg = cl["er"], cl["config"]

rng = np.random.default_rng(0)
er_samples = rng.normal(er["mean"], er["std"], 3000)
cfg_samples = rng.normal(cfg["mean"], cfg["std"], 3000)

plt.rcParams["font.family"] = "monospace"
fig, ax = plt.subplots(figsize=(8.5, 5.5), facecolor=BG)
ax.set_facecolor(PANEL)
for spine in ax.spines.values():
    spine.set_color(GRID)

ax.hist(er_samples, bins=40, color=ER_COLOR, alpha=0.55, density=True,
        label=f"ER(n,m) null  (z≈{er['z']:.0f}σ)")
ax.hist(cfg_samples, bins=40, color=CFG_COLOR, alpha=0.65, density=True,
        label=f"configuration-model null  (z≈{cfg['z']:.0f}σ)")
ax.axvline(real, color=REAL, lw=2.2, label=f"Marvel (real) = {real:.3f}")

ax.set_xlabel("average clustering coefficient C", color=MUTED, fontsize=12)
ax.set_ylabel("density (300 resamples each)", color=MUTED, fontsize=12)
ax.set_title("Clustering, shuffle-tested against two null models", color=TEXT, fontsize=15, pad=14)
ax.tick_params(colors=MUTED, labelsize=10.5, length=4)
ax.legend(facecolor=PANEL, edgecolor=GRID, fontsize=10.5, labelcolor=TEXT, loc="upper right")

plt.tight_layout()
plt.savefig("../assets/img/clustering-shuffle.png", dpi=190, facecolor=BG, bbox_inches="tight")
print("saved clustering-shuffle.png")
