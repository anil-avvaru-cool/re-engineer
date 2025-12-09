# embed/embed_index.py
import json, sys, faiss
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

MODEL="all-MiniLM-L6-v2"

def build_index(chunks_path, index_out, meta_out):
    chunks = json.load(open(chunks_path,"r"))
    texts = [c["text"][:2000] for c in chunks]
    model = SentenceTransformer(MODEL)
    embs = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    # normalize for cosine via inner product
    norms = np.linalg.norm(embs, axis=1, keepdims=True)
    norms[norms==0]=1
    embs = embs / norms
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embs.astype('float32'))
    faiss.write_index(index, index_out)
    json.dump(chunks, open(meta_out,"w"), indent=2)
    print(f"Index written to {index_out} and metadata to {meta_out}")

if __name__ == "__main__":
    build_index(sys.argv[1], sys.argv[2], sys.argv[3])
