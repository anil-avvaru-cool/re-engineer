

# export hcl domino artifacts from nsf database

designer.exe -nosplash -application com.ibm.designer.domino.runDxlExport ^
  -vmargs -DXML.export.source="c:\\DominoExport\\IssueTracker.nsf" ^
          -DXML.export.target="c:\\DominoExport\\IssueTracker.xml" ^
          -DXML.export.type="all"


# create venv and install deps
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# (optional) start Neo4j via docker-compose
docker-compose up -d

# Generate Chunks
python .\ingest\dxl_lss_parser.py .\sample_data\issue_tracker\

# Graph
python graph/chunks_to_neo4j.py --input chunks.json --out ./neo4j --include-lotus-only

# interactive query
python cli/run_query.py --index faiss.index --meta meta.json

# Below are Not used
# run ingestion + index
python ingest/dxl_parser.py sample_data/demo_dxl.xml chunks.json
python parse/lotus_regex_fallback.py chunks.json parsed_chunks.json
python embed/embed_index.py parsed_chunks.json faiss.index meta.json
