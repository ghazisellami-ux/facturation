UPDATE clients SET created_at = '2026-04-18 10:00:00', updated_at = '2026-04-18 10:00:00' WHERE created_at IS NULL;
UPDATE suppliers SET created_at = '2026-04-18 10:00:00', updated_at = '2026-04-18 10:00:00' WHERE created_at IS NULL;
SELECT name, created_at FROM clients;
