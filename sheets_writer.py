from pathlib import Path
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def write_reconciliation_to_sheet(data):
    # google api scope and credentials path
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials_path = Path("credentials/service_account.json")

    # authorise client
    creds = ServiceAccountCredentials.from_json_keyfile_name(str(credentials_path), scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open("ONN1_Reconciliation_Logs")
    worksheet = spreadsheet.sheet1

    # prep header and data row
    headers = [
        "Invoice Number", "Supplier Name", "Job Code",
        "Source Doc Type", "Comparison Doc Type",
        "Status", "Matched Items", "Missing Items", "Extra Items",
        "Discrepancy Count", "Summary"
    ]

    row = [
        data.get("invoice_number"),
        data.get("supplier_name"),
        data.get("job_code"),
        data.get("source_doc_type", "unknown"),
        data.get("comparison_doc_type", "unknown"),
        data.get("reconciliation_status"),
        len(data.get("matched_items", [])),
        len([d for d in data.get("discrepancies", []) if d["type"] == "missing_item"]),
        len([d for d in data.get("discrepancies", []) if d["type"] == "extra_item"]),
        len(data.get("discrepancies", [])),
        data.get("summary")
]


    # add headers if first row is empty
    if not worksheet.cell(1, 1).value:
        worksheet.append_row(headers)

    # append data row
    worksheet.append_row(row)
    print("✅ Reconciliation result written to Google Sheet.")
