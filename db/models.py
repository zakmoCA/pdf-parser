from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    document_type = Column(String, nullable=False)
    document_position = Column(String, nullable=False)
    processing_method = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    parsed_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.timezone.utc)

    reconciliations_as_source = relationship("Reconciliation", foreign_keys="[Reconciliation.source_doc_id]", back_populates="source_document")
    reconciliations_as_comparison = relationship("Reconciliation", foreign_keys="[Reconciliation.comparison_doc_id]", back_populates="comparison_document")

class Reconciliation(Base):
    __tablename__ = "reconciliations"

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String)
    supplier_name = Column(String)
    job_code = Column(String)
    reconciliation_status = Column(String)
    summary = Column(Text)
    discrepancies = Column(Text)
    matched_items = Column(Text)
    processing_method = Column(String, nullable=False)
    source_doc_id = Column(Integer, ForeignKey("documents.id"))
    comparison_doc_id = Column(Integer, ForeignKey("documents.id"))
    created_at = Column(DateTime, default=datetime.timezone.utc)

    source_document = relationship("Document", foreign_keys=[source_doc_id], back_populates="reconciliations_as_source")
    comparison_document = relationship("Document", foreign_keys=[comparison_doc_id], back_populates="reconciliations_as_comparison")
