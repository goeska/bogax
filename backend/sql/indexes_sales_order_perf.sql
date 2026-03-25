-- Performance indexes for sales_order / sales_order_line are created by Django
-- when you run:  python manage.py migrate sales
-- Names (Django ≤30 char limit): idx_so_update_at, idx_so_state_update_at,
-- idx_so_created_by, idx_sol_order_id
--
-- Use this file only if you maintain these tables outside Django and need the
-- same coverage with longer PostgreSQL names:

CREATE INDEX IF NOT EXISTS idx_sales_order_line_sales_order_id_id
  ON sales_order_line (sales_order_id, id);

CREATE INDEX IF NOT EXISTS idx_sales_order_update_at
  ON sales_order (update_at DESC);

CREATE INDEX IF NOT EXISTS idx_sales_order_state_update_at
  ON sales_order (state, update_at DESC);

-- If created_by_id exists:
-- CREATE INDEX IF NOT EXISTS idx_sales_order_created_by_id
--   ON sales_order (created_by_id);
