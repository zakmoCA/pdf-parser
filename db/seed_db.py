import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base, Reconciliation

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def seed():
    session = Session()
    sample = Reconciliation(
        invoice_number="INV-TEST123",
        supplier_name="Test Supplier",
        job_code="JOB-TEST-001",
        status="reconciled",
        summary="Sample reconciliation summary.",
        matched_items=[{"invoice_description": "Thing", "docket_description": "Thing", "quantity": 3}],
        discrepancies=[],
        source_doc_type="Invoice",
        comparison_doc_type="Delivery Docket",
        source_position="first_document",
        comparison_position="second_document"
    )
    session.add(sample)
    session.commit()
    print("Sample record inserted.")

if __name__ == "__main__":
    seed()
