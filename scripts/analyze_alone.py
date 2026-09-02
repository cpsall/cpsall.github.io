# Analysis step for the week-1 post: who's alone, who's cut off together, who's
# the hub. Pure NetworkX, no plotting -- this just computes and reports the
# numbers, then writes them to assets/data/week1-analysis.json so the
# visualization script (make_degree_circle.py) doesn't have to recompute them.

import json
import networkx as nx
import pandas as pd

nodes = pd.read_csv("../../week1_nodes.tsv", sep="\t", comment="#", quoting=3)
edges = pd.read_csv("../../week1_edges.tsv", sep="\t", comment="#", names=["source", "target"])
id_to_name = dict(zip(nodes.node_id, nodes.name))
id_to_desc = dict(zip(nodes.node_id, nodes.description))

G = nx.DiGraph()
G.add_nodes_from(nodes.node_id)
G.add_edges_from(edges.itertuples(index=False))

U = nx.Graph()
U.add_nodes_from(G.nodes)
U.add_edges_from(G.edges)

deg = dict(U.degree())
in_deg = dict(G.in_degree())
out_deg = dict(G.out_degree())

comps = sorted(nx.connected_components(U), key=len, reverse=True)
giant = comps[0]
island = comps[1]
isolates = sorted((list(c)[0] for c in comps if len(c) == 1), key=lambda n: id_to_name[n])

hub_id = max(deg, key=deg.get)
top_in = sorted(in_deg.items(), key=lambda x: x[1], reverse=True)[:5]
top_out = sorted(out_deg.items(), key=lambda x: x[1], reverse=True)[:5]

# Characters known to be famous for reasons a Wikipedia link graph can't see.
famous_despite_isolation = ["Baymax", "Miracleman_(character)", "Yo-Yo_Rodriguez"]

print(f"n = {G.number_of_nodes()} characters, {G.number_of_edges()} directed edges")
print(f"giant component: {len(giant)}")
print(f"sealed-off island: {len(island)} -> {[id_to_name[n] for n in sorted(island)]}")
print(f"alone (degree 0): {len(isolates)}")
for n in isolates:
    flag = "  <-- famous anyway" if n in famous_despite_isolation else ""
    print(f"  - {id_to_name[n]}{flag}")
print(f"hub: {id_to_name[hub_id]}, degree {deg[hub_id]} "
      f"(in={in_deg[hub_id]}, out={out_deg[hub_id]})")
print("top in-degree:", [(id_to_name[n], k) for n, k in top_in])
print("top out-degree:", [(id_to_name[n], k) for n, k in top_out])

report = {
    "n_total": G.number_of_nodes(),
    "n_directed_edges": G.number_of_edges(),
    "hub": {"id": hub_id, "name": id_to_name[hub_id], "degree": deg[hub_id]},
    "giant_component": {"size": len(giant), "members": sorted(giant)},
    "island": {
        "size": len(island),
        "members": sorted(island),
        "names": [id_to_name[n] for n in sorted(island)],
    },
    "isolates": [
        {
            "id": n,
            "name": id_to_name[n],
            "description": id_to_desc[n],
            "famous_despite_isolation": n in famous_despite_isolation,
        }
        for n in isolates
    ],
    "degree": deg,
    "in_degree": in_deg,
    "out_degree": out_deg,
    "top_in_degree": [{"id": n, "name": id_to_name[n], "degree": k} for n, k in top_in],
    "top_out_degree": [{"id": n, "name": id_to_name[n], "degree": k} for n, k in top_out],
}

with open("../assets/data/week1-analysis.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print("\nwrote ../assets/data/week1-analysis.json")
