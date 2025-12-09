
# create venv and install deps
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# (optional) start Neo4j via docker-compose
docker-compose up -d

# run ingestion + index
python ingest/dxl_parser.py sample_data/demo_dxl.xml --out chunks.json
python parse/lotus_extractor.py chunks.json --out parsed_chunks.json
python embed/embed_index.py parsed_chunks.json --index faiss.index --meta meta.json

# interactive query
python cli/run_query.py --index faiss.index --meta meta.json
