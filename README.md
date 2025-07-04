# README

## Capabilities

This project performs automated invoice–delivery docket reconciliation from PDFs using two pipelines:
- GPT-powered parsing and reconciliation
- Native parsing using PyMuPDF and regex logic

## CLI Usage

### GPT-Based Workflow

```bash
# GPT Parse + Reconcile using local uploads
python gpt_parse.py --source uploads
python gpt_reconcile.py --source uploads

# GPT Parse + Reconcile using inbox
python gpt_parse.py --source inbox
python gpt_reconcile.py --source inbox
```

### Native Workflow (Regex-based)

```bash
# Native Parse + Reconcile using local uploads
python parse_pdfs.py --source uploads
python reconcile.py --source uploads

# Native Parse + Reconcile using inbox
python parse_pdfs.py --source inbox
python reconcile.py --source inbox
```

## Output Structure

Dynamically routed to one of:

```
local_src_gpt_output/
local_src_native_output/
email_src_gpt_output/
email_src_native_output/
```

Each includes:

```
/parsed     → Raw text + parsed JSON
/reconciled → Final reconciliation results (.json + .txt)
```

Emails are sent upon reconciliation, and discrepancies are logged to a google sheet for future alerting.

---

### GPT Outputs (Sample)

**`sample_invoice_parsed.json`**
```json
{
  "invoice_number": "INV-4567",
  "supplier_name": "SupplierX Pty Ltd",
  "job_code": "JOB-ONN1-901",
  "document_type": "invoice",
  "line_items": [
    {
      "description": "GPO Single Power Outlet",
      "quantity": 15,
      "unit_price": 18
    },
    {
      "description": "CAT6 Data Cable (10m)",
      "quantity": 7,
      "unit_price": 9.5
    },
    {
      "description": "2-Gang Switch Plate",
      "quantity": 4,
      "unit_price": 13
    }
  ],
  "document_position": "first_document",
  "raw_text": "..."
}
```

**`sample_delivery_docket_parsed.json`**
```json
{
  "invoice_number": "INV-4567",
  "supplier_name": "SupplierX Pty Ltd",
  "job_code": "JOB-ONN1-901",
  "document_type": "delivery_docket",
  "line_items": [
    {
      "description": "Power Outlet - GPO",
      "quantity": 15
    },
    {
      "description": "CAT6 Cable - 10m",
      "quantity": 7
    },
    {
      "description": "Switch Plate - 2 Gang",
      "quantity": 4
    }
  ],
  "document_position": "second_document",
  "raw_text": "..."
}
```



**GPT-parsed Invoice text**

```txt
Supplier Invoice 
Supplier: SupplierX Pty Ltd​
Invoice Number: INV-4567​
Date: 2025-06-20​
Job Code: JOB-ONN1-901​
 
Items:​
1. GPO Single Power Outlet | Qty: 15 | Unit Price: $18.00​
2. CAT6 Data Cable (10m) | Qty: 7 | Unit Price: $9.50​
3. 2-Gang Switch Plate | Qty: 4 | Unit Price: $13.00​
​
Subtotal: $352.50​
GST (10%): $35.25​
Total: $387.75​
Total: $387.75​
```

**GPT-parsed  Delivery Docket (source) text**

```txt
Delivery Docket 
Supplier: SupplierX Pty Ltd​
Delivery Docket - Reference INV-4567​
Date Delivered: 2024-06-21​
Job Code: JOB-ONN1-901​
​
Delivered Items:​
1. Power Outlet - GPO | Qty: 15​
2. CAT6 Cable - 10m | Qty: 7​
3. Switch Plate - 2 Gang | Qty: 4​
```
---

### Native (PyMuPDF & Regex-Based) Outputs

**`sample_invoice_parsed.json`**
```json
{
  "invoice_number": "INV-4567",
  "supplier_name": "SupplierX Pty Ltd",
  "job_code": "JOB-ONN1-901",
  "line_items": [
    {
      "description": "GPO Single Power Outlet",
      "quantity": 15,
      "unit_price": 18.0
    },
    {
      "description": "CAT6 Data Cable (10m)",
      "quantity": 7,
      "unit_price": 9.5
    },
    {
      "description": "2-Gang Switch Plate",
      "quantity": 4,
      "unit_price": 13.0
    }
  ],
  "document_type": "invoice",
  "document_position": "first_document"
}
```

**`source_parsed.json (deliver_docket)`**

```json
{
  "invoice_number": "INV-4567",
  "supplier_name": "SupplierX Pty Ltd",
  "job_code": "JOB-ONN1-901",
  "line_items": [
    {
      "description": "Power Outlet - GPO",
      "quantity": 15
    },
    {
      "description": "CAT6 Cable - 10m",
      "quantity": 7
    },
    {
      "description": "Switch Plate - 2 Gang",
      "quantity": 4
    }
  ],
  "document_type": "delivery_docket",
  "document_position": "second_document"
}
```


**Natively parsed Invoice text**

```txt
Supplier Invoice 
Supplier: SupplierX Pty Ltd​
Invoice Number: INV-4567​
Date: 2025-06-20​
Job Code: JOB-ONN1-901​
 
Items:​
1. GPO Single Power Outlet | Qty: 15 | Unit Price: $18.00​
2. CAT6 Data Cable (10m) | Qty: 7 | Unit Price: $9.50​
3. 2-Gang Switch Plate | Qty: 4 | Unit Price: $13.00​
​
Subtotal: $352.50​
GST (10%): $35.25​
Total: $387.75​
```

**Natively parsed Delivery Docket text**

```txt
Delivery Docket 
Supplier: SupplierX Pty Ltd​
Delivery Docket - Reference INV-4567​
Date Delivered: 2024-06-21​
Job Code: JOB-ONN1-901​
​
Delivered Items:​
1. Power Outlet - GPO | Qty: 15​
2. CAT6 Cable - 10m | Qty: 7​
3. Switch Plate - 2 Gang | Qty: 4​
​```
```
​


## Email Integration

Fetches the latest email with PDF attachment(s) and invoice-related keywords in the subject, body, or filename. Uses IMAP via Gmail.



## API Integrations

- **OpenAI API** – GPT-4.1 for document parsing and reconciliation
- **Gmail IMAP** – To fetch attachments
- **Google Sheets API** – To log reconciliation results
- **PostgreSQL** – For document metadata and audit logging





