# chunk/chunker.py
import json, hashlib

def id_for(chunk):
    return hashlib.sha1((chunk.get("source","") + chunk.get("name","") + chunk.get("text","")).encode()).hexdigest()

def normalize(inpath, outpath):
    chunks = json.load(open(inpath))
    out=[]
    seen=set()
    for c in chunks:
        cid = id_for(c)
        if cid in seen:
            continue
        seen.add(cid)
        c["id"] = cid
        c["tokens"] = len(c["text"].split())
        out.append(c)
    json.dump(out, open(outpath,"w"), indent=2)
    print(f"{len(out)} normalized chunks -> {outpath}")

if __name__ == "__main__":
    import sys
    normalize(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else "norm_chunks.json")
