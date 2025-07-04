import argparse
from pathlib import Path
from dotenv import load_dotenv
from utils.email_utils import fetch_relevant_pdf_attachments
from utils.document_matcher import find_matching_document
from gpt_parse import main as gpt_parse_main
from gpt_reconcile import main as gpt_reconcile_main
from parse_pdfs import main as native_parse_main
from reconcile import main as native_reconcile_main

load_dotenv()

def determine_output_dirs(source: str, method: str):
    base_name = f"{'local_src' if source == 'uploads' else 'email_src'}_{method}_output"
    parsed_dir = Path(base_name) / "parsed"
    reconciled_dir = Path(base_name) / "reconciled"
    parsed_dir.mkdir(parents=True, exist_ok=True)
    reconciled_dir.mkdir(parents=True, exist_ok=True)
    return parsed_dir, reconciled_dir

def main():
    parser = argparse.ArgumentParser(description="Run document parsing and reconciliation.")
    parser.add_argument("--source", choices=["uploads", "inbox"], default="uploads", help="PDF input source")
    parser.add_argument("--method", choices=["gpt", "native"], default="gpt", help="Processing method")
    args = parser.parse_args()

    parsed_dir, reconciled_dir = determine_output_dirs(args.source, args.method)

    if args.source == "uploads":
        uploads_dir = Path("uploads")
        invoice_pdf = uploads_dir / "sample_invoice.pdf"
        delivery_pdf = uploads_dir / "sample_delivery_docket.pdf"
    else:
        paths = fetch_relevant_pdf_attachments(Path("email_uploads"))
        if len(paths) < 1:
            print("No PDFs matched in email inbox.")
            return
        invoice_pdf = paths[0]
        delivery_pdf = paths[1] if len(paths) > 1 else None

    if args.method == "gpt":
        gpt_parse_main()
        gpt_reconcile_main()
    else:
        native_parse_main()
        native_reconcile_main()

if __name__ == "__main__":
    main()
