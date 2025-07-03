from pathlib import Path
import pymupdf  # PyMuPDF
import json
import re
import unicodedata

def extract_text(pdf_path):
    try:
        doc = pymupdf.open(pdf_path)
        return "\n".join(page.get_text() for page in doc).strip()
    except Exception as e:
        return f"error reading {pdf_path}: {e}"

def clean_text(text):  # strip invisible characters like \u200b
    return unicodedata.normalize("NFKC", text).replace("\u200b", "").strip()

def write_to_file(content, out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")

def parse_metadata_and_line_items(text):
    result = {
        "invoice_number": None,
        "supplier_name": None,
        "job_code": None,
        "line_items": []
    }

    match = re.search(r"Supplier:\s*(.+)", text)
    result["supplier_name"] = clean_text(match.group(1)) if match else None

    invoice_patterns = [
        r"Invoice\s+(?:Number|No\.?):\s*(INV-\d+)",  # Invoice Number: or Invoice No.: examples
        r"\b(INV-\d+)\b"  # Standalone INV-xxxx example, reference for later use in project
    ]
    for pattern in invoice_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["invoice_number"] = clean_text(match.group(1 if match.lastindex else 0))
            break

    # Job Code
    match = re.search(r"Job Code:\s*(\S+)", text)
    result["job_code"] = clean_text(match.group(1)) if match else None

    # Line Items
    invoice_item_pattern = re.compile(
        r"\d+\.\s*(.*?)\s*\|\s*Qty:\s*(\d+)\s*\|\s*Unit Price:\s*\$?([\d.]+)",
        re.IGNORECASE
    )

    delivery_item_pattern = re.compile(
        r"\d+\.\s*(.*?)\s*\|\s*Qty:\s*(\d+)",
        re.IGNORECASE
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
    output = Path("output")
    output.mkdir(exist_ok=True)

    invoice_path = uploads / "sample_invoice.pdf"
    source_path = uploads / "sample_delivery_docket.pdf"

    if not invoice_path.exists() or not source_path.exists():
        print("!! one or both pdf files are missing.")
        return

    invoice_text = extract_text(invoice_path)
    source_text = extract_text(source_path)

    write_to_file(invoice_text, output / "invoice_text.txt")
    write_to_file(source_text, output / "source_text.txt")

    invoice_json = parse_metadata_and_line_items(invoice_text)
    source_json = parse_metadata_and_line_items(source_text)

    write_to_file(json.dumps(invoice_json, indent=2), output / "invoice_parsed.json")
    write_to_file(json.dumps(source_json, indent=2), output / "source_parsed.json")

    print("✅ extracted and parsed files saved to /output")

if __name__ == "__main__":
    main()
