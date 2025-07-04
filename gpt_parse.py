from pathlib import Path
import pymupdf
import json
import unicodedata
from openai import OpenAI
from dotenv import load_dotenv
import os
import argparse
from utils.email_utils import fetch_relevant_pdf_attachments

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    if "invoice" in lowered:
        return "invoice"
    elif "delivery docket" in lowered:
        return "delivery_docket"
    elif "purchase confirmation" in lowered:
        return "purchase_confirmation"
    return "unknown"

def parse_with_gpt(raw_text: str) -> dict:
    doc_type = detect_document_type(raw_text)
    prompt = f"""
You are a document parser. Extract the following structured information from this invoice, delivery docket, or purchase confirmation text. Return a clean, valid JSON.

Fields to extract:
- invoice_number (e.g., INV-1234)
- supplier_name
- job_code (if present)
- document_type: one of "invoice", "delivery_docket", "purchase_confirmation", or "unknown"
- line_items: a list of items, where each item includes:
  - description
  - quantity (integer)
  - unit_price (number, optional)
  - line_total (number, optional)

Text:
\"\"\"
{raw_text}
\"\"\"
"""
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    result = response.choices[0].message.content.strip()
    try:
        parsed = json.loads(result)
        parsed["document_type"] = doc_type
        return parsed
    except json.JSONDecodeError:
        print("!! GPT response was not valid JSON. Here's the raw response:")
        print(result)
        return {}

def main():
    uploads = Path("uploads")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["uploads", "inbox"], default="uploads")
    args = parser.parse_args()

    base_dir = Path("local_src_gpt_output") if args.source == "uploads" else Path("email_src_gpt_output")
    gpt_parsed_output = base_dir / "parsed"
    gpt_parsed_output.mkdir(parents=True, exist_ok=True)

    invoice_path = uploads / "sample_invoice.pdf"
    source_path = uploads / "sample_delivery_docket.pdf"

    if not invoice_path.exists() or not source_path.exists():
        print("!! one or both PDF files are missing.")
        return

    invoice_text = clean_text(extract_text(invoice_path))
    source_text = clean_text(extract_text(source_path))

    write_to_file(invoice_text, gpt_parsed_output / "invoice_text.txt")
    write_to_file(source_text, gpt_parsed_output / "source_text.txt")

    print("🤖 Parsing invoice with GPT...")
    invoice_json = parse_with_gpt(invoice_text)
    invoice_json["document_type"] = detect_document_type(invoice_text)
    invoice_json["document_position"] = "first_document"
    
    print("🤖 Parsing source/docket with GPT...")
    source_json = parse_with_gpt(source_text)
    source_json["document_type"] = detect_document_type(source_text)
    source_json["document_position"] = "second_document"
    
    write_to_file(json.dumps(invoice_json, indent=2), gpt_parsed_output / "invoice_parsed.json")
    write_to_file(json.dumps(source_json, indent=2), gpt_parsed_output / "source_parsed.json")

    print("✅ Done! Parsed files saved to /gpt_output/parsed")

if __name__ == "__main__":
    main()
