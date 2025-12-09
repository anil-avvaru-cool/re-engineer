# cli/run_query.py
import json, sys, faiss
from sentence_transformers import SentenceTransformer
import numpy as np

MODEL="all-MiniLM-L6-v2"

def load_index(idx_path):
    return faiss.read_index(idx_path)

def query(index, meta_path, query_text, top_k=5):
    chunks = json.load(open(meta_path))
    model = SentenceTransformer(MODEL)
    qv = model.encode([query_text], convert_to_numpy=True)[0]
    qv = qv / (np.linalg.norm(qv) + 1e-12)
    D, I = index.search(qv.reshape(1,-1).astype('float32'), top_k)
    results = []
    for dist, i in zip(D[0], I[0]):
        c = chunks[int(i)]
        results.append((float(dist), c))
    return results

if __name__ == "__main__":
    idx = sys.argv[1]
    meta = sys.argv[2]
    index = load_index(idx)
    while True:
        q = input("Query> ").strip()
        if not q:
            continue
        if q.lower() in ("exit","quit"):
            break
        res = query(index, meta, q, top_k=5)
        for score, c in res:
            print(f"\nSCORE: {score:.4f}  NAME: {c.get('name')}  ID: {c.get('id')}")
            print(c["text"][:800])
        # assemble a short RAG prompt
        prompt = "Question: " + q + "\n\nContext:\n"
        for score, c in res:
            prompt += f"---\nFile: {c.get('name')} (id:{c.get('id')})\n{c['text'][:1200]}\n"
        prompt += "\nAnswer concisely with side-effects and external deps."
        print("\n-- RAG prompt (copy to your LLM) --\n")
        print(prompt)
