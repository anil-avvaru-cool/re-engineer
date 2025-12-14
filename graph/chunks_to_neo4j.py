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

def classify_artifact(path: str):
    p = path.lower()
    if "agent" in p:
        return "Agent"
    if "lib" in p:
        return "ScriptLibrary"
    if "form" in p:
        return "Form"
    return "Artifact"

# -------------------------------------------------
# CLI
# -------------------------------------------------
def main():
    argp = argparse.ArgumentParser(
        description="Generate Neo4j-ready dependency graph from chunks.json"
    )
    argp.add_argument("--input", "-i", required=True)
    argp.add_argument("--out", "-o", default="neo4j")
    args = argp.parse_args()

    os.makedirs(args.out, exist_ok=True)

    with open(args.input, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    procedures = {}
    artifacts = {}

    # -------------------------------------------------
    # Build in-memory model
    # -------------------------------------------------
    for c in chunks:
        if c.get("language") != "LotusScript":
            continue

        proc_id = c["id"]
        proc_name = c.get("metadata", {}).get("name", proc_id)
        file_path = c.get("file_path", "unknown")

        procedures[proc_id] = {
            "id": proc_id,
            "name": proc_name,
            "file_path": file_path,
            "complexity": int(c.get("complexity", 0)),
            "size": int(c.get("size_bytes", 0)),
            "calls": parse_calls(c.get("content", ""))
        }

        if file_path not in artifacts:
            artifacts[file_path] = {
                "id": f"artifact_{uuid.uuid4().hex[:8]}",
                "path": file_path,
                "type": classify_artifact(file_path)
            }

    # -------------------------------------------------
    # Artifact Nodes
    # -------------------------------------------------
    with open(os.path.join(args.out, "artifact_nodes.csv"), "w", encoding="utf-8") as f:
        f.write("id:ID,type,path\n")
        for a in artifacts.values():
            f.write(f"{a['id']},{a['type']},{a['path']}\n")

    # -------------------------------------------------
    # Procedure Nodes
    # -------------------------------------------------
    with open(os.path.join(args.out, "procedure_nodes.csv"), "w", encoding="utf-8") as f:
        f.write("id:ID,name,file_path,complexity,size\n")
        for p in procedures.values():
            f.write(
                f"{p['id']},{p['name']},{p['file_path']},{p['complexity']},{p['size']}\n"
            )

    # -------------------------------------------------
    # Relationships
    # -------------------------------------------------
    with open(os.path.join(args.out, "relationships.csv"), "w", encoding="utf-8") as f:
        f.write(":START_ID,:END_ID,:TYPE\n")

        # DEFINED_IN
        for p in procedures.values():
            artifact = artifacts[p["file_path"]]
            f.write(f"{p['id']},{artifact['id']},DEFINED_IN\n")

        # CALLS
        for p in procedures.values():
            for callee in p["calls"]:
                for target in procedures.values():
                    if target["name"].lower() == callee.lower():
                        f.write(f"{p['id']},{target['id']},CALLS\n")

    print("Neo4j CSV generation completed")
    print(f"Artifacts: {len(artifacts)}")
    print(f"Procedures: {len(procedures)}")

# -------------------------------------------------
if __name__ == "__main__":
    main()
