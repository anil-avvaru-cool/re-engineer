import os
import re
import json
import uuid
import sys
import xml.etree.ElementTree as ET


# -------------------- UTILITIES --------------------

def uid(prefix, name):
    return f"{prefix}_{name}_{uuid.uuid4().hex[:8]}"

def file_stats(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    return {
        "line_count": len(lines),
        "size_bytes": os.path.getsize(path),
        "text": "".join(lines)
    }

def calc_complexity(text):
    score = 0
    score += len(re.findall(r"\bIf\b|\bElseIf\b", text, re.IGNORECASE))
    score += 2 * len(re.findall(r"\bFor\b|\bWhile\b|\bDo\b", text, re.IGNORECASE))
    score += 2 * len(re.findall(r"\bSelect\s+Case\b", text, re.IGNORECASE))
    score += len(re.findall(r"\bCall\b", text, re.IGNORECASE))
    score += len(re.findall(r"On\s+Error", text, re.IGNORECASE))
    return score

def extract_dependencies(text):
    return re.findall(r'Use\s+"([^"]+)"', text, re.IGNORECASE)


# -------------------- LOTUSSCRIPT PARSER --------------------

def parse_lss(path):
    stats = file_stats(path)
    text = stats["text"]
    chunks = []

    dependencies = extract_dependencies(text)

    # File-level chunk
    chunks.append({
        "id": uid("lss_file", os.path.basename(path)),
        "type": "lotusscript_file",
        "file_path": path,
        "language": "LotusScript",
        "size_bytes": stats["size_bytes"],
        "line_count": stats["line_count"],
        "complexity": calc_complexity(text),
        "dependencies": dependencies,
        "content": f"LotusScript file {os.path.basename(path)} containing agents or shared logic.",
        "metadata": {
            "dependencies": dependencies
        }
    })

    # Extract Subs / Functions
    pattern = re.compile(
        r"(Sub|Function)\s+(\w+).*?(End\s+\1)",
        re.IGNORECASE | re.DOTALL
    )

    for m in pattern.finditer(text):
        block = m.group(0)
        name = m.group(2)

        chunks.append({
            "id": uid("lss_block", name),
            "type": m.group(1).lower(),
            "file_path": path,
            "language": "LotusScript",
            "size_bytes": len(block.encode("utf-8")),
            "line_count": block.count("\n") + 1,
            "complexity": calc_complexity(block),
            "dependencies": dependencies,
            "content": block.strip(),
            "metadata": {
                "name": name,
                "parent_file": os.path.basename(path)
            }
        })

    return chunks


# -------------------- DXL PARSER --------------------

def parse_dxl(path):
    stats = file_stats(path)
    text = stats["text"]
    chunks = []

    root = ET.fromstring(text)

    # FORM
    form = root.find(".//form")
    if form is not None:
        name = form.findtext("name")

        chunks.append({
            "id": uid("form", name),
            "type": "form",
            "file_path": path,
            "language": "DXL",
            "size_bytes": stats["size_bytes"],
            "line_count": stats["line_count"],
            "complexity": len(form.findall("items/item")),
            "dependencies": [],
            "content": f"Domino Form {name} defining Issue document structure.",
            "metadata": {
                "form_name": name
            }
        })

        for item in form.findall("items/item"):
            field_name = item.get("name")
            field_type = "text"
            if item.find("richtext") is not None:
                field_type = "richtext"
            elif item.find("datetime") is not None:
                field_type = "datetime"

            chunks.append({
                "id": uid("field", field_name),
                "type": "field",
                "file_path": path,
                "language": "DXL",
                "size_bytes": len(ET.tostring(item)),
                "line_count": 1,
                "complexity": 1,
                "dependencies": [],
                "content": f"Field {field_name} of type {field_type}.",
                "metadata": {
                    "field_name": field_name,
                    "field_type": field_type,
                    "form": name
                }
            })

    # VIEW
    view = root.find(".//view")
    if view is not None:
        name = view.findtext("name")
        chunks.append({
            "id": uid("view", name),
            "type": "view",
            "file_path": path,
            "language": "DXL",
            "size_bytes": stats["size_bytes"],
            "line_count": stats["line_count"],
            "complexity": len(view.findall(".//column")),
            "dependencies": [],
            "content": f"Domino View {name} used for issue filtering and presentation.",
            "metadata": {
                "view_name": name
            }
        })

    return chunks


# -------------------- DIRECTORY SCANNER --------------------

def parse_repository(root_dir):
    all_chunks = []

    for root, _, files in os.walk(root_dir):
        for f in files:
            path = os.path.join(root, f)
            rel = os.path.relpath(path, root_dir)

            if f.lower().endswith(".lss"):
                all_chunks.extend(parse_lss(path))
            elif f.lower().endswith(".dxl"):
                all_chunks.extend(parse_dxl(path))

    return all_chunks


# -------------------- MAIN --------------------

if __name__ == "__main__":
    input_dir = "sample_data\\issue_tracker"
    ROOT = input_dir
    chunks = parse_repository(ROOT)

    with open("chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    print(f"Generated {len(chunks)} chunks.")
