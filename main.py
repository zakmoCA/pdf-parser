from pathlib import Path
import pymupdf

def extract_text(pdf_path):
    try:
        doc = pymupdf.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        return f"❌ Error reading {pdf_path}: {e}"

def main():
    invoice_path = Path("uploads") / "sample_invoice.pdf"
    source_path = Path("uploads") / "sample_delivery_docket.pdf"

    if not invoice_path.exists() or not source_path.exists():
        print("one or both pdf files are missing in the uploads folder.")
        print(f"expected files:\n - {invoice_path}\n - {source_path}")
        return

    print(f"\n📄 reading: {invoice_path.name}")
    invoice_text = extract_text(invoice_path)
    print(invoice_text or "[no text found]")

    print("\n" + "=" * 80 + "\n") 

    print(f"📄 reading: {source_path.name}")
    source_text = extract_text(source_path)
    print(source_text or "[no text found]")

if __name__ == "__main__":
    main()
