# ingest/dxl_parser.py
import sys, json
from lxml import etree

def parse_dxl_to_chunks(dxl_path):
    tree = etree.parse(dxl_path)
    root = tree.getroot()
    chunks = []
    # agents
    for agent in root.findall(".//agent"):
        name = agent.get("name") or "agent"
        ls = agent.find(".//lotusscript")
        if ls is not None and ls.text:
            chunks.append({
                "id": f"agent:{name}",
                "type": "agent",
                "name": name,
                "source": "dxl",
                "text": ls.text
            })
    # forms events
    for evt in root.findall(".//event"):
        name = evt.get("name") or "event"
        ls = evt.find(".//lotusscript")
        if ls is not None and ls.text:
            chunks.append({
                "id": f"formevent:{name}",
                "type": "form_event",
                "name": name,
                "source": "dxl",
                "text": ls.text
            })
    return chunks

if __name__ == "__main__":
    dxl = sys.argv[1]
    out = sys.argv[2] if len(sys.argv)>2 else "chunks.json"
    chunks = parse_dxl_to_chunks(dxl)
    with open(out,"w",encoding="utf-8") as fh:
        json.dump(chunks,fh,indent=2)
    print(f"Wrote {len(chunks)} chunks to {out}")
