# Analysis step for the week-2 posts: random-graph / configuration-model /
# Watts-Strogatz comparisons against the real Marvel network from week 1.
# Mirrors the pattern of analyze_alone.py -- pure computation, no plotting,
# writes everything needed by the week-2 plotting scripts to
# assets/data/week2-analysis.json.

import json, random, warnings
import numpy as np
import pandas as pd
import networkx as nx
import powerlaw

warnings.filterwarnings("ignore")
RNG_SEED = 42
random.seed(RNG_SEED)
np.random.seed(RNG_SEED)
rng = np.random.default_rng(RNG_SEED)

DATA_DIR = "../.."  # site/scripts -> site -> repo root, where week1_nodes.tsv / week1_edges.tsv live
nodes = pd.read_csv(f"{DATA_DIR}/week1_nodes.tsv", sep="\t", comment="#", quoting=3)
edges = pd.read_csv(f"{DATA_DIR}/week1_edges.tsv", sep="\t", comment="#", names=["source", "target"])
id_to_name = dict(zip(nodes.node_id, nodes.name))

G = nx.DiGraph()
G.add_nodes_from(nodes.node_id)
G.add_edges_from(edges.itertuples(index=False))

U = nx.Graph()
U.add_nodes_from(G.nodes)
U.add_edges_from(G.edges)

n_total, m_total = U.number_of_nodes(), U.number_of_edges()
deg_full = dict(U.degree())
in_deg = dict(G.in_degree())
out_deg = dict(G.out_degree())

comps = sorted(nx.connected_components(U), key=len, reverse=True)
giant_nodes, island_nodes = comps[0], comps[1]
isolate_nodes = [list(c)[0] for c in comps if len(c) == 1]

Gc = U.subgraph(giant_nodes).copy()
n, m = Gc.number_of_nodes(), Gc.number_of_edges()
deg_seq_giant = [d for _, d in Gc.degree()]
full_deg_seq_ordered = [deg_full[nid] for nid in U.nodes()]
node_list = list(U.nodes())
idx_of = {nid: i for i, nid in enumerate(node_list)}

C_real = nx.average_clustering(Gc)
T_real = nx.transitivity(Gc)
L_real = nx.average_shortest_path_length(Gc)
k_avg_full = 2 * m_total / n_total
k_avg_giant = 2 * m / n

def sample_stat(n_samples, builder, statfunc, seed0):
    return np.array([statfunc(builder(seed0 + i)) for i in range(n_samples)])

def avg_L_safe(Gi):
    if nx.is_connected(Gi):
        return nx.average_shortest_path_length(Gi)
    gc = max(nx.connected_components(Gi), key=len)
    return nx.average_shortest_path_length(Gi.subgraph(gc))

def config_model_simple(deg_seq, seed):
    Gm = nx.configuration_model(deg_seq, seed=seed)
    Gs = nx.Graph(Gm)
    Gs.remove_edges_from(nx.selfloop_edges(Gs))
    return Gs

def z_and_p(real, null):
    z = (real - null.mean()) / null.std()
    return float(z), float((null >= real).mean())

N = 300
print("running ER / configuration-model nulls on the giant component...")
er_C  = sample_stat(N, lambda s: nx.gnm_random_graph(n, m, seed=s), nx.average_clustering, 10_000)
er_T  = sample_stat(N, lambda s: nx.gnm_random_graph(n, m, seed=s), nx.transitivity, 20_000)
er_L  = sample_stat(100, lambda s: nx.gnm_random_graph(n, m, seed=s), avg_L_safe, 30_000)
cfg_C = sample_stat(N, lambda s: config_model_simple(deg_seq_giant, s), nx.average_clustering, 40_000)
cfg_T = sample_stat(N, lambda s: config_model_simple(deg_seq_giant, s), nx.transitivity, 50_000)
cfg_L = sample_stat(100, lambda s: config_model_simple(deg_seq_giant, s), avg_L_safe, 60_000)

z_er_C, p_er_C   = z_and_p(C_real, er_C)
z_cfg_C, p_cfg_C = z_and_p(C_real, cfg_C)
z_er_T, p_er_T   = z_and_p(T_real, er_T)
z_cfg_T, p_cfg_T = z_and_p(T_real, cfg_T)

print("running isolate-count nulls on the full 303-node degree sequence...")
iso_cfg = sample_stat(N, lambda s: config_model_simple(full_deg_seq_ordered, s), nx.number_of_isolates, 70_000)
iso_er  = sample_stat(N, lambda s: nx.gnm_random_graph(n_total, m_total, seed=s), nx.number_of_isolates, 80_000)

print("testing whether the 9-node island survives as a clean separate group...")
def island_escapes(seed):
    Gm = nx.configuration_model(full_deg_seq_ordered, seed=seed)
    Gs = nx.Graph(Gm); Gs.remove_edges_from(nx.selfloop_edges(Gs))
    island_idx = {idx_of[nid] for nid in island_nodes}
    for i in island_idx:
        for nbr in Gs.neighbors(i):
            if nbr not in island_idx:
                return True
    return False
island_escape_flags = [island_escapes(90_000 + i) for i in range(N)]
island_escape_rate = float(np.mean(island_escape_flags))

Gisland = U.subgraph(island_nodes).copy()
island_connected = nx.is_connected(Gisland)
island_degrees = {id_to_name[nid]: d for nid, d in Gisland.degree()}
island_internal_edges = list(Gisland.edges())

outside_giant = list(giant_nodes)
def single_edge_merges(trials=500, seed0=1):
    merged = 0
    for t in range(trials):
        rnd = random.Random(seed0 + t)
        a = rnd.choice(list(island_nodes))
        b = rnd.choice(outside_giant)
        Uc = U.copy(); Uc.add_edge(a, b)
        gc = max(nx.connected_components(Uc), key=len)
        merged += int(set(island_nodes) <= gc)
    return merged / trials
single_edge_merge_rate = single_edge_merges()

outside_any = [nid for nid in U.nodes() if nid not in island_nodes]
def rewire_k_outward(k, trials=200, seed0=100_000):
    merged, zero_deg = 0, []
    for t in range(trials):
        rnd = random.Random(seed0 + t)
        Uc = U.copy()
        chosen = rnd.sample(island_internal_edges, k) if k <= len(island_internal_edges) else island_internal_edges
        for (a, b) in chosen:
            if not Uc.has_edge(a, b):
                continue
            Uc.remove_edge(a, b)
            new_target = rnd.choice(outside_any)
            tries = 0
            while (new_target == a or Uc.has_edge(a, new_target)) and tries < 50:
                new_target = rnd.choice(outside_any); tries += 1
            Uc.add_edge(a, new_target)
        zero_deg.append(sum(1 for nid in island_nodes if Uc.degree(nid) == 0))
        gc = max(nx.connected_components(Uc), key=len)
        merged += int(set(island_nodes) <= gc)
    return merged / trials, float(np.mean(zero_deg))

print("sweeping outward-rewire count on the island's own edges...")
rewire_curve = []
for k in range(0, len(island_internal_edges) + 1):
    frac, zd = rewire_k_outward(k)
    rewire_curve.append({"k": k, "merge_fraction": frac, "avg_stranded": zd})

# ---------- degree-distribution model comparison ----------
print("building ER and BA comparison networks (matched n & m)...")
G_er_full = nx.gnm_random_graph(n_total, m_total, seed=RNG_SEED)
G_ba_full = nx.barabasi_albert_graph(n_total, 5, seed=RNG_SEED)  # m=5 -> ~1490 edges, close to m_total=1434

def ccdf(degrees):
    x = np.sort(degrees)
    nn = len(x)
    uniq = np.unique(x)
    p = np.array([(x >= k).sum() / nn for k in uniq])
    return uniq.tolist(), p.tolist()

deg_marvel = np.array([d for d in deg_full.values() if d > 0])
deg_er = np.array([d for _, d in G_er_full.degree() if d > 0])
deg_ba = np.array([d for _, d in G_ba_full.degree() if d > 0])

k_marvel, p_marvel = ccdf(deg_marvel)
k_er, p_er = ccdf(deg_er)
k_ba, p_ba = ccdf(deg_ba)

print("fitting power law (CSN / MLE) to Marvel in-degree...")
in_degrees = np.array([d for d in in_deg.values() if d > 0])
fit = powerlaw.Fit(in_degrees, discrete=True, verbose=False)
R_ln, p_ln = fit.distribution_compare('power_law', 'lognormal')
R_exp, p_exp = fit.distribution_compare('power_law', 'exponential')
csn = {
    "alpha": round(float(fit.power_law.alpha), 3),
    "xmin": int(fit.power_law.xmin),
    "sigma": round(float(fit.power_law.sigma), 3),
    "R_vs_lognormal": round(float(R_ln), 2),
    "p_vs_lognormal": float(p_ln),
    "R_vs_exponential": round(float(R_exp), 2),
    "p_vs_exponential": float(p_exp),
}
print(csn)

# ---------- GCC phase transition, n = 303, marking real <k> ----------
print("sweeping the giant-component phase transition (n=303)...")
def giant_fraction(n_, p_, seed):
    Gp = nx.gnp_random_graph(n_, p_, seed=seed)
    return len(max(nx.connected_components(Gp), key=len)) / n_

k_grid = np.round(np.arange(0.2, 12.01, 0.6), 2)
phase_means, phase_stds = [], []
for kk in k_grid:
    p_ = kk / (n_total - 1)
    fracs = [giant_fraction(n_total, p_, int(rng.integers(1_000_000_000))) for _ in range(20)]
    phase_means.append(float(np.mean(fracs))); phase_stds.append(float(np.std(fracs)))

# ---------- Watts-Strogatz sweep, matched to the giant component's size & mean degree ----------
print("sweeping Watts-Strogatz q (n=277, k~10)...")
n_ws = n
k_ws = int(round(k_avg_giant / 2) * 2)  # nearest even
qs = [0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0]
ws_C_means, ws_C_stds, ws_L_means, ws_L_stds = [], [], [], []
for q in qs:
    Cs, Ls = [], []
    for _ in range(20):
        seed = int(rng.integers(1_000_000_000))
        Gw = nx.connected_watts_strogatz_graph(n_ws, k_ws, q, tries=500, seed=seed)
        Cs.append(nx.average_clustering(Gw))
        Ls.append(nx.average_shortest_path_length(Gw))
    ws_C_means.append(float(np.mean(Cs))); ws_C_stds.append(float(np.std(Cs)))
    ws_L_means.append(float(np.mean(Ls))); ws_L_stds.append(float(np.std(Ls)))

report = {
    "n_total": n_total, "m_total": m_total, "k_avg_full": k_avg_full,
    "giant": {"n": n, "m": m, "k_avg": k_avg_giant, "C": C_real, "T": T_real, "L": L_real,
              "members": sorted(giant_nodes)},
    "island": {"n": len(island_nodes), "m": len(island_internal_edges),
               "names": [id_to_name[nid] for nid in island_nodes],
               "degrees": island_degrees, "connected": bool(island_connected),
               "density": len(island_internal_edges) / (len(island_nodes)*(len(island_nodes)-1)/2)},
    "isolates": {"count": len(isolate_nodes), "names": [id_to_name[n_] for n_ in isolate_nodes]},
    "nulls": {
        "clustering": {"real": C_real,
                        "er": {"mean": float(er_C.mean()), "std": float(er_C.std()), "z": z_er_C, "p": p_er_C, "samples": er_C.tolist()},
                        "config": {"mean": float(cfg_C.mean()), "std": float(cfg_C.std()), "z": z_cfg_C, "p": p_cfg_C, "samples": cfg_C.tolist()}},
        "transitivity": {"real": T_real,
                          "er": {"mean": float(er_T.mean()), "std": float(er_T.std()), "z": z_er_T, "p": p_er_T},
                          "config": {"mean": float(cfg_T.mean()), "std": float(cfg_T.std()), "z": z_cfg_T, "p": p_cfg_T}},
        "path_length": {"real": L_real, "er_mean": float(er_L.mean()), "config_mean": float(cfg_L.mean())},
        "isolate_count": {"real": len(isolate_nodes),
                           "er": {"mean": float(iso_er.mean()), "std": float(iso_er.std())},
                           "config": {"mean": float(iso_cfg.mean()), "std": float(iso_cfg.std())}},
    },
    "island_experiments": {
        "escape_rate_under_config_reshuffle": island_escape_rate,
        "single_outward_edge_merge_rate": single_edge_merge_rate,
        "rewire_curve": rewire_curve,
    },
    "degree_distribution": {
        "marvel": {"k": k_marvel, "p": p_marvel},
        "er": {"k": k_er, "p": p_er},
        "ba": {"k": k_ba, "p": p_ba},
        "csn_fit": csn,
    },
    "phase_transition": {"k_grid": k_grid.tolist(), "mean": phase_means, "std": phase_stds,
                          "marvel_k": k_avg_full},
    "watts_strogatz": {"n": n_ws, "k": k_ws, "q": qs,
                        "C_mean": ws_C_means, "C_std": ws_C_stds,
                        "L_mean": ws_L_means, "L_std": ws_L_stds,
                        "marvel_C": C_real, "marvel_L": L_real},
}

with open("../assets/data/week2-analysis.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print("\nwrote week2-analysis.json")
