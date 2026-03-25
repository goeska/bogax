-- =============================================================================
-- sales_order.created_by_id — multi-user & audit (LEGACY / manual upgrade)
-- =============================================================================
-- Tabel sales_order yang dibuat lewat ``python manage.py migrate sales`` sudah
-- menyertakan created_by_id. Jalankan skrip ini hanya untuk DB lama yang
-- dibuat sebelum migrasi Django, atau jika migrate belum pernah dijalankan.
--
-- Jalankan sebagai user DB yang punya hak ALTER pada tabel sales_order.
--
-- FK mengarah ke: public.accounts_user(id)
--   Itu tabel user Django Anda (AUTH_USER_MODEL = "accounts.User").
-- Tipe: BIGINT — sama dengan tipe kolom id di accounts_user (Django BigAutoField).
--
-- Kolom boleh NULL dulu agar baris lama (sebelum audit) tetap valid.
-- Setelah semua baris punya pemilik, Anda bisa (opsional) mengunci NOT NULL:
--   UPDATE sales_order SET created_by_id = <user_id_default> WHERE created_by_id IS NULL;
--   ALTER TABLE sales_order ALTER COLUMN created_by_id SET NOT NULL;
-- =============================================================================

BEGIN;

ALTER TABLE sales_order
    ADD COLUMN IF NOT EXISTS created_by_id BIGINT NULL;

-- Hindari duplikat constraint jika skrip dijalankan ulang
ALTER TABLE sales_order
    DROP CONSTRAINT IF EXISTS sales_order_created_by_id_fkey;

ALTER TABLE sales_order
    ADD CONSTRAINT sales_order_created_by_id_fkey
    FOREIGN KEY (created_by_id)
    REFERENCES accounts_user (id)
    ON DELETE RESTRICT;

-- Mempercepat filter/list per user & JOIN ke accounts_user
CREATE INDEX IF NOT EXISTS idx_sales_order_created_by_id
    ON sales_order (created_by_id);

COMMENT ON COLUMN sales_order.created_by_id IS
    'User (accounts_user.id) yang membuat order; FK untuk multi-user & audit.';

COMMIT;
