from sqlalchemy.orm import Session
from models import Document, Reconciliation

def create_document(db: Session, filename, doc_type, position, method, content, parsed_json=None):
    doc = Document(
        filename=filename,
        document_type=doc_type,
        document_position=position,
        processing_method=method,
        content=content,
        parsed_json=parsed_json
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def create_reconciliation(db: Session, invoice_number, supplier_name, job_code, status, summary, discrepancies, matched_items, method, source_doc_id, comparison_doc_id):
    recon = Reconciliation(
        invoice_number=invoice_number,
        supplier_name=supplier_name,
        job_code=job_code,
        reconciliation_status=status,
        summary=summary,
        discrepancies=discrepancies,
        matched_items=matched_items,
        processing_method=method,
        source_doc_id=source_doc_id,
        comparison_doc_id=comparison_doc_id
    )
    db.add(recon)
    db.commit()
    db.refresh(recon)
    return recon
