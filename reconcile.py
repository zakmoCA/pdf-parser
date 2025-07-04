import json
from pathlib import Path
from difflib import SequenceMatcher
import argparse

def compare_line_items(invoice_items, delivery_items, fuzzy_threshold=0.8):
    discrepancies = []
    matched = []

    delivery_pool = delivery_items.copy()

    def find_best_match(inv_desc):
        best_score = 0
        best_match = None
        for d in delivery_pool:
            score = SequenceMatcher(None, inv_desc.lower(), d['description'].lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = d
        return best_match if best_score >= fuzzy_threshold else None

    for invoice_item in invoice_items:
        inv_desc = invoice_item['description']
        inv_qty = invoice_item['quantity']

        match = find_best_match(inv_desc)
        if not match:
            discrepancies.append({
                "description": inv_desc,
                "issue": "Missing from delivery document"
            })
            continue

        if match['quantity'] != inv_qty:
            discrepancies.append({
                "description": inv_desc,
                "invoice_qty": inv_qty,
                "delivered_qty": match['quantity'],
                "issue": "Quantity mismatch"
            })
        else:
            matched.append(invoice_item)

        delivery_pool.remove(match)

    for leftover in delivery_pool:
        discrepancies.append({
            "description": leftover['description'],
            "issue": "Extra item in delivery not invoiced"
        })

    return matched, discrepancies

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["uploads", "inbox"], default="uploads")
    args = parser.parse_args()

    base_dir = Path("local_src_native_output") if args.source == "uploads" else Path("email_src_native_output")
    parsed_output_dir = base_dir / "parsed"
    reconciled_output_dir = base_dir / "reconciled"
    reconciled_output_dir.mkdir(parents=True, exist_ok=True)

    invoice_json_path = parsed_output_dir / "invoice_parsed.json"
    source_json_path = parsed_output_dir / "source_parsed.json"

    if not invoice_json_path.exists() or not source_json_path.exists():
        print("❌ Missing parsed JSON files. Run parsing first.")
        return

    with open(invoice_json_path) as f:
        invoice_data = json.load(f)

    with open(source_json_path) as f:
        source_data = json.load(f)

    matched, discrepancies = compare_line_items(
        invoice_data.get("line_items", []),
        source_data.get("line_items", [])
    )

    with open(reconciled_output_dir / "matched_items.json", "w") as f:
        json.dump(matched, f, indent=2)

    with open(reconciled_output_dir / "discrepancies.json", "w") as f:
        json.dump(discrepancies, f, indent=2)

    print("✅ Reconciliation complete.")
    print(f"✅ {len(matched)} matched items")
    print(f"⚠️  {len(discrepancies)} discrepancies found")

if __name__ == "__main__":
    main()
