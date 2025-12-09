# parse/lotus_regex_fallback.py
import re, json, sys

SUB_RE = re.compile(r'^(Sub\s+\w+.*?End\s+Sub)', re.IGNORECASE | re.MULTILINE | re.DOTALL)
FUNC_RE = re.compile(r'^(Function\s+\w+.*?End\s+Function)', re.IGNORECASE | re.MULTILINE | re.DOTALL)

def extract_subs_from_text(text):
    matches = []
    for m in SUB_RE.finditer(text):
        matches.append(m.group(1).strip())
    for m in FUNC_RE.finditer(text):
        matches.append(m.group(1).strip())
    return matches

if __name__ == "__main__":
    inpath = sys.argv[1] if len(sys.argv)>1 else "chunks.json"
    outpath = sys.argv[2] if len(sys.argv)>2 else "parsed_chunks.json"
    chunks = json.load(open(inpath,"r"))
    parsed=[]
    for c in chunks:
        subs = extract_subs_from_text(c["text"])
        if subs:
            for i,s in enumerate(subs):
                parsed.append({
                    "id": f"{c['id']}:sub:{i}",
                    "type": c.get("type"),
                    "name": c.get("name"),
                    "text": s,
                    "source": c.get("source","dxl")
                })
        else:
            parsed.append(c)
    json.dump(parsed, open(outpath,"w"), indent=2)
    print(f"Wrote {len(parsed)} parsed chunks to {outpath}")
