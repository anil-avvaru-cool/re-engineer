#!/usr/bin/env python3
import json
import uuid
import argparse
import os
import tree_sitter_lotus
import tree_sitter

# -------------------------------------------------
# Tree-sitter setup
# -------------------------------------------------
parser = tree_sitter.Parser()
#parser.set_language(tree_sitter_lotus.language())
language = tree_sitter.Language(tree_sitter_lotus.language())
parser.language = language

# -------------------------------------------------
# AST utilities
# -------------------------------------------------
def parse_calls(code: str):
    """
    Extract procedure calls from LotusScript using AST.
    """
    tree = parser.parse(code.encode("utf-8"))
    root = tree.root_node
    calls = set()

    stack = [root]
    while stack:
        node = stack.pop()
        if node.type == "call_statement":
            text = code[node.start_byte:node.end_byte]
            parts = text.strip().split()
            if len(parts) > 1:
                calls.add(parts[1])
        stack.extend(node.children)

    return sorted(calls)

# -------------------------------------------------
# CLI
# -------------------------------------------------
def main():
    argp = argparse.ArgumentParser(
        description="Convert chunks.json into Neo4j dependency graph using tree-sitter-lotus"
    )
    argp.add_argument(
        "--input", "-i",
        required=True,
        help="Path to chunks.json"
    )
    argp.add_argument(
        "--out", "-o",
        default="neo4j",
        help="Output directory for Neo4j CSV files"
    )
    argp.add_argument(
        "--include-lotus-only",
        action="store_true",
        help="Process only LotusScript chunks"
    )

    args = argp.parse_args()

    os.makedirs(args.out, exist_ok=True)

    with open(args.input, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    procedures = {}
    artifacts = {}

    # -------------------------------------------------
    # Build nodes
    # -------------------------------------------------
    for c in chunks:
        if args.include_lotus_only and c.get("language") != "LotusScript":
            continue

        if c.get("language") != "LotusScript":
            continue

        proc_id = c["id"]
        proc_name = c.get("metadata", {}).get("name", proc_id)
        file_path = c.get("file_path", "unknown")

        procedures[proc_id] = {
            "id": proc_id,
            "name": proc_name,
            "file_path": file_path,
            "complexity": c.get("complexity", 0),
            "size": c.get("size_bytes", 0),
            "calls": parse_calls(c.get("content", ""))
        }

        if file_path not in artifacts:
            artifacts[file_path] = {
                "id": f"artifact_{uuid.uuid4().hex[:8]}",
                "path": file_path
            }

    # -------------------------------------------------
    # Write Neo4j Nodes CSV
    # -------------------------------------------------
    nodes_path = os.path.join(args.out, "nodes.csv")
    with open(nodes_path, "w", encoding="utf-8") as f:
        f.write("id:ID,label,name,file_path,complexity,size\n")

        for a in artifacts.values():
            f.write(f"{a['id']},Artifact,,{a['path']},,\n")

        for p in procedures.values():
            f.write(
                f"{p['id']},Procedure,{p['name']},{p['file_path']},{p['complexity']},{p['size']}\n"
            )

    # -------------------------------------------------
    # Write Neo4j Relationships CSV
    # -------------------------------------------------
    rels_path = os.path.join(args.out, "relationships.csv")
    with open(rels_path, "w", encoding="utf-8") as f:
        f.write(":START_ID,:END_ID,:TYPE\n")

        # DEFINED_IN
        for p in procedures.values():
            artifact = artifacts[p["file_path"]]
            f.write(f"{p['id']},{artifact['id']},DEFINED_IN\n")

        # CALLS
        for p in procedures.values():
            for callee in p["calls"]:
                for target in procedures.values():
                    if target["name"] == callee:
                        f.write(f"{p['id']},{target['id']},CALLS\n")

    print("Neo4j graph generated successfully")
    print(f"Nodes: {nodes_path}")
    print(f"Relationships: {rels_path}")

# -------------------------------------------------
if __name__ == "__main__":
    main()
