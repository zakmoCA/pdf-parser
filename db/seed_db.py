from .database import SessionLocal
from . import models, crud

def seed():
    """
    seeds db with with two sample docs + one reconciliation record
    """
    db = SessionLocal()

    print("seeding database...")
    
    doc1 = crud.create_document(
        db=db,
        filename="sample_invoice.pdf",
        document_type="invoice",
        parsed_json={
            "invoice_number": "INV-SEED123",
            "supplier_name": "Seed Supplier Inc.",
            "job_code": "JOB-SEED-01",
            "line_items": [{"description": "Test Item A", "quantity": 10}]
        }
    )
    print(f"created document with ID: {doc1.id}")

    doc2 = crud.create_document(
        db=db,
        filename="sample_delivery_docket.pdf",
        document_type="delivery_docket",
        parsed_json={
            "invoice_number": "INV-SEED123",
            "supplier_name": "Seed Supplier Inc.",
            "job_code": "JOB-SEED-01",
            "line_items": [{"description": "Test Item A", "quantity": 10}]
        }
    )
    print(f"created document with ID: {doc2.id}")

    # reconciliation record that links the two documents
    reconciliation_result = {
        "invoice_number": "INV-SEED123",
        "supplier_name": "Seed Supplier Inc.",
        "job_code": "JOB-SEED-01",
        "reconciliation_status": "reconciled",
        "summary": "This is a sample reconciliation created via the seeder.",
        "discrepancies": [],
        "matched_items": [{"description": "Test Item A", "quantity": 10}]
    }

    recon = crud.create_reconciliation(
        db=db,
        doc1=doc1,
        doc2=doc2,
        result=reconciliation_result,
        method="gpt-4.1"
    )
    
    print(f"created reconciliation with ID: {recon.id}")
    print("seeding complete ✅")

    db.close()

if __name__ == "__main__":
    seed()