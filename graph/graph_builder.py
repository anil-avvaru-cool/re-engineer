# graph/graph_builder.py
import json, re
from collections import defaultdict

CALL_RE = re.compile(r'\b([A-Za-z_]\w+)\s*\(', re.MULTILINE)

def build_graph(meta_path, out_json="graph.json"):
    chunks = json.load(open(meta_path))
    name_map = {}
    for c in chunks:
        # try to detect sub/function name from first line
        first = c["text"].splitlines()[0]
        m = re.search(r'(Sub|Function)\s+(\w+)', first, re.IGNORECASE)
        if m:
            name_map[c["id"]] = m.group(2)
        else:
            name_map[c["id"]] = c.get("name", c["id"][:8])
    edges = []
    for c in chunks:
        callers = CALL_RE.findall(c["text"])
        for call in callers:
            # naive: if any chunk name equals call, create edge
            for tid, tname in name_map.items():
                if tname.lower() == call.lower() and tid != c["id"]:
                    edges.append({"from": c["id"], "to": tid, "call": call})
    graph = {"nodes":[{"id":k,"name":v} for k,v in name_map.items()], "edges": edges}
    json.dump(graph, open(out_json,"w"), indent=2)
    print(f"Graph written to {out_json}, nodes: {len(name_map)}, edges: {len(edges)}")

if __name__ == "__main__":
    import sys
    build_graph(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else "graph.json")
