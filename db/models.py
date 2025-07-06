from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

Base = declarative_base()

class Document(Base):
    """
    this represents a single ingested pdf document
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    document_type = Column(String)  # e.g., 'invoice', 'delivery_docket'
    
    # stores the structured data extracted by the gpt/native parser 
    parsed_json = Column(JSONB)
    
    # reconciliation this document is part of FK
    reconciliation_id = Column(Integer, ForeignKey("reconciliations.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.timezone.utc)

    reconciliation = relationship("Reconciliation", back_populates="documents")


class Reconciliation(Base):
    """
    this represents the outcome of comparing two documents
    """
    __tablename__ = "reconciliations"

    id = Column(Integer, primary_key=True)
    
    # key identifiers for quick lookups as extracted from documents
    invoice_number = Column(String, index=True)
    supplier_name = Column(String)
    job_code = Column(String, index=True)
    
    reconciliation_status = Column(String, nullable=False) # ...'pending', 'reconciled', 'mismatch' etc
    processing_method = Column(String, nullable=False) # gpt-path or native-path
    summary = Column(String)
    
    # store as lists of objects as json for querying
    discrepancies = Column(JSONB)
    matched_items = Column(JSONB)
    
    created_at = Column(DateTime, default=datetime.timezone.utc)

    documents = relationship("Document", back_populates="reconciliation")