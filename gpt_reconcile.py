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

You will be provided two documents — typically a supplier invoice and a delivery docket — each in two formats:
1. A structured JSON version parsed via regex
2. The raw text extracted from the original PDF

Your objectives are:
1. Extract any missing key identifiers (e.g. invoice number, supplier name, job code) if absent from the JSON using the raw text.
2. Compare the line items from the two documents and assess whether they match.
   - Use flexible matching logic: description phrasing may vary, but should be semantically aligned.
   - Compare quantity across both sides.
   - Ignore unit price in delivery docket (if missing), but flag if it's present and inconsistent.
3. Identify and output discrepancies such as:
   - Mismatched quantities
   - Missing items (present in invoice, missing in delivery)
   - Extra items (present in delivery, missing in invoice)
   - Duplicate charges (multiple lines referring to the same item)
4. Summarize whether the reconciliation is successful (no discrepancies) or failed (one or more issues found).

Return a structured JSON result like this inside a json file:
{{
  "invoice_number": "...",
  "job_code": "...",
  "supplier_name": "...",
  "reconciliation_status": "reconciled" | "mismatch",
  "matched_items": [
    {{
      "invoice_description": "...",
      "docket_description": "...",
      "quantity": ...
    }}
  ],
  "discrepancies": [
    {{
      "type": "missing_item" | "extra_item" | "quantity_mismatch" | "duplicate",
      "invoice_description": "...",
      "docket_description": "...",
      "expected_quantity": ...,
      "found_quantity": ...,
      "notes": "..."
    }}
  ],
  "summary": "e.g. 3 matched, 1 missing, 0 extra",
  "original_invoice_json": {json.dumps(invoice_data)},
  "original_delivery_json": {json.dumps(delivery_data)}
}}


Also return a .txt file with the explanation (max 200 words) summarising your findings and judgment on the reconciliation outcome. This will be used for audit logging and human review.

Both the output .json and .txt files should be named with the convention "invoice number" + "reconciled", or "mismatch" respectively depending on the outcome.

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
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        gpt_output = response.choices[0].message.content
        return gpt_output

    except Exception as e:
        return f"!! GPT reconciliation failed: {e}"

def clean_gpt_summary(raw_text):
    lines = raw_text.strip().splitlines()
    clean_lines = []

    for line in lines:
        stripped = line.strip()
        # skip lines like markdown separators or GPT annotation
        if stripped in ("---", "```"):
            continue
        if stripped.startswith("**Output") and stripped.endswith("**"):
            continue
        clean_lines.append(line)  # preserve original line (including empty)

    return "\n".join(clean_lines).strip()



def main():
    output_dir = Path("output")
    invoice_json_path = output_dir / "invoice_parsed.json"
    delivery_json_path = output_dir / "source_parsed.json"
    invoice_txt_path = output_dir / "invoice_text.txt"
    delivery_txt_path = output_dir / "source_text.txt"

    result = reconcile_with_gpt(invoice_json_path, delivery_json_path, invoice_txt_path, delivery_txt_path)

    out_dir = output_dir / "gpt_reconciliation"
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        # extract the json from the gpt response
        json_start = result.find("{")
        json_end = result.rfind("}") + 1
        json_str = result[json_start:json_end]
        parsed = json.loads(json_str)

        # extract file name components
        invoice_number = parsed.get("invoice_number", "unknown").replace("/", "-")
        status = parsed.get("reconciliation_status", "unknown")
        base_name = f"{invoice_number}_{status}"

        # save json file
        with open(out_dir / f"{base_name}.json", "w") as f:
            json.dump(parsed, f, indent=2)

        # extract plain-text summary (everything outside the JSON)
        raw_text_summary = result[json_end:]
        text_summary = clean_gpt_summary(raw_text_summary) # clean txt summary output of GPTisms in output

        with open(out_dir / f"{base_name}.txt", "w") as f:
            f.write(text_summary)


        print(f"✅ Reconciliation complete. Saved:\n- {base_name}.json\n- {base_name}.txt")

    except Exception as e:
        # fallback if GPT output not well formatted
        fallback_path = out_dir / "gpt_summary_raw.txt"
        with open(fallback_path, "w") as f:
            f.write(result)
        print("⚠️ GPT output not parsable. Raw output saved:", fallback_path)


if __name__ == "__main__":
    main()
