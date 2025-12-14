

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
python graph/chunks_to_neo4j.py --input chunks.json --out ./neo4j

```cipher
CREATE CONSTRAINT artifact_id IF NOT EXISTS
FOR (p:Artifact) REQUIRE p.id IS UNIQUE;
```

```cipher
CREATE CONSTRAINT procedure_id IF NOT EXISTS
FOR (p:Procedure) REQUIRE p.id IS UNIQUE;
```


```cipher
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/anil-avvaru-cool/re-engineer/refs/heads/main/neo4j/artifact_nodes.csv' AS row
MERGE (:Artifact {id: row.id})
SET
  _.type = row.type,
  _.path = row.path;

```

```cipher
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/anil-avvaru-cool/re-engineer/refs/heads/main/neo4j/procedure_nodes.csv' AS row
MERGE (:Procedure {id: row.id})
SET
  _.name = row.name,
  _.file_path = row.file_path,
  _.complexity = toInteger(row.complexity),
  _.size = toInteger(row.size);
```
```cipher

```




# interactive query
python cli/run_query.py --index faiss.index --meta meta.json

# Neo4j tutorial
https://www.youtube.com/watch?v=8jNPelugC2s&t=597s

# Below are Not used, old approach
# run ingestion + index
python ingest/dxl_parser.py sample_data/demo_dxl.xml chunks.json
python parse/lotus_regex_fallback.py chunks.json parsed_chunks.json
python embed/embed_index.py parsed_chunks.json faiss.index meta.json
