# parse/lotus_extractor.py (tree-sitter skeleton)
from tree_sitter import Language, Parser
import json

# Build the tree-sitter library once:
# Language.build_library('build/lotus.so', ['path/to/tree-sitter-lotus'])

LOTUS = Language('build/lotus.so', 'lotusscript')
parser = Parser()
parser.set_language(LOTUS)

def extract_subs(code):
    tree = parser.parse(code.encode())
    root = tree.root_node
    subs=[]
    for node in root.walk():
        # depends on grammar node types; pseudo-code
        if node.type in ("sub_declaration","function_declaration"):
            start = node.start_byte; end = node.end_byte
            subs.append(code[start:end].decode('utf-8'))
    return subs

if __name__ == "__main__":
    chunks = json.load(open("chunks.json","r"))
    out=[]
    for c in chunks:
        subs = extract_subs(c["text"])
        if subs:
            for s in subs:
                out.append({**c, "text": s})
        else:
            out.append(c)
    json.dump(out, open("parsed_chunks.json","w"), indent=2)
    print("Parsed chunks written.")
