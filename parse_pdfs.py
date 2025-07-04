from pathlib import Path
import pymupdf
import json
import re
import unicodedata
import argparse
from utils.email_utils import fetch_relevant_pdf_attachments

def extract_text(pdf_path):
    try:
        doc = pymupdf.open(pdf_path)
        return "\n".join(page.get_text() for page in doc).strip()
    except Exception as e:
        return f"error reading {pdf_path}: {e}"

def clean_text(text):
    return unicodedata.normalize("NFKC", text).replace("\u200b", "").strip()

def write_to_file(content, out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")

def detect_document_type(text):
    lowered = text.lower()
    if "delivery docket" in lowered:
        return "delivery_docket"
    elif "purchase confirmation" in lowered:
        return "purchase_confirmation"
    elif "invoice" in lowered:
        return "invoice"
    else:
        return "unknown"

def parse_metadata_and_line_items(text, position_label):
    result = {
        "invoice_number": None,
        "supplier_name": None,
        "job_code": None,
        "line_items": [],
        "document_type": detect_document_type(text),
        "document_position": position_label
    }

    match = re.search(r"Supplier:\s*(.+)", text)
    result["supplier_name"] = clean_text(match.group(1)) if match else None

    invoice_patterns = [
        r"Invoice\s+(?:Number|No\.?):\s*(INV-\d+)",
        r"\b(INV-\d+)\b"
    ]
    for pattern in invoice_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["invoice_number"] = clean_text(match.group(1 if match.lastindex else 0))
            break

    match = re.search(r"Job Code:\s*(\S+)", text)
    result["job_code"] = clean_text(match.group(1)) if match else None

    invoice_item_pattern = re.compile(
        r"\d+\.\s*(.*?)\s*\|\s*Qty:\s*(\d+)\s*\|\s*Unit Price:\s*\$?([\d.]+)", re.IGNORECASE
    )
    delivery_item_pattern = re.compile(
        r"\d+\.\s*(.*?)\s*\|\s*Qty:\s*(\d+)", re.IGNORECASE
    )

    matches = invoice_item_pattern.findall(text)
    if matches:
        for match in matches:
            description, qty, price = match
            result["line_items"].append({
                "description": description.strip(),
                "quantity": int(qty),
                "unit_price": float(price)
            })
    else:
        for match in delivery_item_pattern.findall(text):
            description, qty = match
            result["line_items"].append({
                "description": description.strip(),
                "quantity": int(qty)
            })

    return result

def main():
    uploads = Path("uploads")
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["uploads", "inbox"], default="uploads")
    args = parser.parse_args()

    base_dir = Path("local_src_native_output") if args.source == "uploads" else Path("email_src_native_output")
    output = base_dir / "parsed"
    output.mkdir(parents=True, exist_ok=True)

    invoice_path = uploads / "sample_invoice.pdf"
    source_path = uploads / "sample_delivery_docket.pdf"

    if not invoice_path.exists() or not source_path.exists():
        print("!! one or both pdf files are missing.")
        return

    invoice_text = extract_text(invoice_path)
    source_text = extract_text(source_path)

    write_to_file(invoice_text, output / "invoice_text.txt")
    write_to_file(source_text, output / "source_text.txt")

    invoice_json = parse_metadata_and_line_items(invoice_text, "first_document")
    source_json = parse_metadata_and_line_items(source_text, "second_document")

    write_to_file(json.dumps(invoice_json, indent=2), output / "invoice_parsed.json")
    write_to_file(json.dumps(source_json, indent=2), output / "source_parsed.json")

    print("✅ extracted and parsed files saved to /output")

if __name__ == "__main__":
    main()
