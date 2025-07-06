from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_
from . import models

def create_document(db: Session, filename: str, document_type: str, parsed_json: dict):
    """
    creates a new document record in the database
    """
    doc = models.Document(
        filename=filename,
        document_type=document_type,
        parsed_json=parsed_json
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def find_unmatched_document(db: Session, doc_to_match: models.Document):
    """
    finds a doc in db that has not yet been reconciled +
    matches the key identifiers of the provided doc
    """
    new_doc_identifiers = doc_to_match.parsed_json or {}
    inv_num = new_doc_identifiers.get('invoice_number')
    job_code = new_doc_identifiers.get('job_code')

    if not inv_num and not job_code:
        return None

    # buils a query to find a document that
    query = db.query(models.Document).filter(
        models.Document.reconciliation_id.is_(None), # ---> has not been assigned to a reconciliation yet 
        models.Document.id != doc_to_match.id, # ---> is not the same document we are trying to match
        or_(
            models.Document.parsed_json['invoice_number'].astext == inv_num if inv_num else False,
            models.Document.parsed_json['job_code'].astext == job_code if job_code else False
        ) # ---> has a matching invoice_number or job_code inside its parsed_json
    )
    
    return query.first()


def create_reconciliation(db: Session, doc1: models.Document, doc2: models.Document, result: dict, method: str):
    """
    creates a reconciliation record and links the two source documents to it
    """
    # create the reconciliation entry
    recon = models.Reconciliation(
        invoice_number=result.get("invoice_number"),
        supplier_name=result.get("supplier_name"),
        job_code=result.get("job_code"),
        reconciliation_status=result.get("reconciliation_status"),
        summary=result.get("summary"),
        discrepancies=result.get("discrepancies", []),
        matched_items=result.get("matched_items", []),
        processing_method=method
    )
    
    # add the docs to the reconciliation
    recon.documents.append(doc1)
    recon.documents.append(doc2)
    
    db.add(recon)
    db.commit()
    db.refresh(recon)
    return recon