-- Fix null created_at on existing invoices
UPDATE invoices SET created_at = '2026-04-28 10:00:00' WHERE created_at IS NULL;
UPDATE invoices SET updated_at = '2026-04-28 10:00:00' WHERE updated_at IS NULL;

-- Add client: centre tlili
INSERT INTO clients (id, company_id, name, tax_id, city, country, contact_name, balance)
VALUES (
  '6891e011-6dc0-4077-954b-43395714d328',
  '95d72a55-b35a-4e3e-b697-d657ef14e995',
  'centre tlili d''imagerie médicale Gafsa',
  '1959059DAM000',
  'Gafsa',
  'Tunisie',
  'Jamel Tlili',
  0
) ON CONFLICT (id) DO NOTHING;

-- Add invoice: FAC cabinet Tlili (8331 TND)
INSERT INTO invoices (id, company_id, client_id, reference, invoice_type, status, date, due_date, subtotal, discount_amount, tva_amount, fodec_amount, timbre_fiscal, total, amount_paid, balance_due, currency, created_at, updated_at)
VALUES (
  'ac247759-00af-454e-b5ca-e8cf9fdfa6f0',
  '95d72a55-b35a-4e3e-b697-d657ef14e995',
  '6891e011-6dc0-4077-954b-43395714d328',
  'FAC-20260003',
  'facture',
  'payee',
  '2026-04-18',
  '2026-04-28',
  7000, 0, 1330, 0, 1, 8331, 0, 8331, 'TND',
  '2026-04-18 10:00:00',
  '2026-04-18 10:00:00'
) ON CONFLICT (id) DO NOTHING;

-- Add invoice item: vitre plombée
INSERT INTO invoice_items (id, invoice_id, description, quantity, unit, unit_price, discount_percent, tva_rate, fodec_rate, subtotal, tva_amount, fodec_amount, total, sort_order)
VALUES (
  '87fbc665-c786-4aab-879e-97b109df2e5c',
  'ac247759-00af-454e-b5ca-e8cf9fdfa6f0',
  'Vitre plombée médical dimensions 80x60cm (fourniture et pose)',
  2, 'unité', 3500, 0, 19, 0, 7000, 1330, 0, 8330, 0
) ON CONFLICT (id) DO NOTHING;
