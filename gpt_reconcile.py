from pathlib import Path
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def reconcile_with_gpt(invoice_json_path, delivery_json_path, invoice_txt_path, delivery_txt_path):
    try:
        with open(invoice_json_path) as f:
            invoice_data = json.load(f)
        with open(delivery_json_path) as f:
            delivery_data = json.load(f)
        with open(invoice_txt_path) as f:
            invoice_text = f.read()
        with open(delivery_txt_path) as f:
            delivery_text = f.read()

        prompt = f"""
You are an accounts reconciliation assistant.

You will be provided two documents, each in two formats:
1. A structured JSON (from our parser)
2. The raw text content extracted from the original PDF

Each document represents either:
- an invoice
- or a delivery docket

Your task is to:
- Extract any metadata that might be missing in the JSON from the raw text (e.g. invoice number, job code, supplier name)
- Compare line items from the two documents
- Identify discrepancies such as:
    - quantity mismatches
    - missing items
    - extra items not found in invoice
- Use your judgment to match similar descriptions (e.g. "2-Gang Switch" ≈ "Switch Plate - 2 Gang")

Your output should be a JSON object with:
{{
  "matched_items": [...],
  "discrepancies": [...],
  "summary": "2 matched, 1 missing, 1 extra"
}}

Here is the structured invoice:
```json
{json.dumps(invoice_data, indent=2)}
```

Here is the raw invoice text:
```
{invoice_text}
```

Here is the structured delivery docket:
```json
{json.dumps(delivery_data, indent=2)}
```

Here is the raw delivery docket text:
```
{delivery_text}
```
        """.strip()

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        gpt_output = response.choices[0].message.content
        return gpt_output

    except Exception as e:
        return f"!! GPT reconciliation failed: {e}"

def main():
    output_dir = Path("output")
    invoice_json_path = output_dir / "invoice_parsed.json"
    delivery_json_path = output_dir / "source_parsed.json"
    invoice_txt_path = output_dir / "invoice_text.txt"
    delivery_txt_path = output_dir / "source_text.txt"

    result = reconcile_with_gpt(invoice_json_path, delivery_json_path, invoice_txt_path, delivery_txt_path)

    out_file = output_dir / "reconciliation" / "gpt_summary.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        parsed = json.loads(result)
        with open(out_file, "w") as f:
            json.dump(parsed, f, indent=2)
        print("✅ GPT reconciliation complete. Saved to:", out_file)
    except Exception:
        with open(out_file.with_suffix(".txt"), "w") as f:
            f.write(result)
        print("⚠️ GPT response saved as raw text (not valid JSON).")

if __name__ == "__main__":
    main()
