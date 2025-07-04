-- mock documents
INSERT INTO documents (document_type, document_position, invoice_number, job_code, supplier_name, raw_text, parsed_json)
VALUES
('invoice', 'first_document', 'INV-0001', 'JC-100', 'Supplier A', 'Raw invoice text', '{}'),
('delivery_docket', 'second_document', 'INV-0001', 'JC-100', 'Supplier A', 'Raw delivery text', '{}');

-- mock reconciliation entry
INSERT INTO reconciliations (invoice_document_id, source_document_id, reconciliation_status, matched_items, discrepancies, summary)
VALUES
(1, 2, 'reconciled', '[]', '[]', '2 matched, 0 discrepancies');
