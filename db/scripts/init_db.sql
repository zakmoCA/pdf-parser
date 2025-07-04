CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    document_type TEXT NOT NULL,
    document_position TEXT NOT NULL,
    processing_method TEXT NOT NULL,
    content TEXT NOT NULL,
    parsed_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reconciliations (
    id SERIAL PRIMARY KEY,
    invoice_number TEXT,
    supplier_name TEXT,
    job_code TEXT,
    reconciliation_status TEXT,
    summary TEXT,
    discrepancies TEXT,
    matched_items TEXT,
    processing_method TEXT NOT NULL,
    source_doc_id INTEGER REFERENCES documents(id),
    comparison_doc_id INTEGER REFERENCES documents(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
