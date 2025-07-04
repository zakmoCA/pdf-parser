from pathlib import Path
import json
from typing import Optional, Tuple

def load_parsed_documents(parsed_dir: Path):
    parsed_docs = []
    for file in parsed_dir.glob("*.json"):
        with open(file) as f:
            data = json.load(f)
            parsed_docs.append((file, data))
    return parsed_docs

def extract_identifiers(doc: dict) -> Tuple[Optional[str], Optional[str]]:
    return doc.get("invoice_number"), doc.get("job_code")

def documents_match(doc1: dict, doc2: dict) -> bool:
    inv1, job1 = extract_identifiers(doc1)
    inv2, job2 = extract_identifiers(doc2)
    return any([
        inv1 and inv1 == inv2,
        inv1 and inv1 == job2,
        job1 and job1 == inv2,
        job1 and job1 == job2
    ])

def find_matching_document(new_doc: dict, parsed_dir: Path) -> Optional[Tuple[Path, dict]]:
    for existing_path, existing_doc in load_parsed_documents(parsed_dir):
        if documents_match(new_doc, existing_doc):
            return existing_path, existing_doc
    return None, None
