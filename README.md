# demo-microservices

Three intentionally small services sharing one Postgres schema, built as the
"real code" for the `db-change-agent` project's Impact Analysis Agent to
statically analyze and for its PR Agent to open pull requests against.

- `orders-service` — place/ship/cancel orders, stock check before ordering
- `refunds-service` — request/approve/reject refunds; reads `orders.total_amount`
- `inventory-service` — stock decrement on order, restock on approved refund;
  reads from both `orders` and `refunds`

The cross-service reads (e.g. refunds-service reading `orders.total_amount`,
inventory-service joining `refunds` to `orders`) are deliberate: they give the
Impact Analysis Agent real dependencies to detect when a column on `orders`
changes, rather than a trivial one-service-per-table demo.

Schema: `shared-schema/schema.sql`.
