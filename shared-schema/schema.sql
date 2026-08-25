-- Shared demo schema for the DML Change Impact & Approval Agent project.
-- Three services (orders, refunds, inventory) share this Postgres schema,
-- deliberately with realistic cross-service column dependencies so the
-- Impact Analysis Agent has something real to detect.

CREATE TABLE IF NOT EXISTS orders (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    product_id      BIGINT NOT NULL,
    quantity        INTEGER NOT NULL,
    status          TEXT NOT NULL DEFAULT 'placed',   -- placed | shipped | cancelled
    total_amount    NUMERIC(10, 2) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS refunds (
    id              BIGSERIAL PRIMARY KEY,
    order_id        BIGINT NOT NULL REFERENCES orders(id),
    user_id         BIGINT NOT NULL,
    amount          NUMERIC(10, 2) NOT NULL,
    reason          TEXT,
    status          TEXT NOT NULL DEFAULT 'pending',  -- pending | approved | rejected
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS inventory (
    id                  BIGSERIAL PRIMARY KEY,
    product_id          BIGINT NOT NULL,
    warehouse_id        BIGINT NOT NULL,
    quantity            INTEGER NOT NULL,
    reorder_threshold   INTEGER NOT NULL DEFAULT 10,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
