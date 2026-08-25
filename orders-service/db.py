"""
orders-service: owns order placement, status updates and lookups.
Queries are written as plain SQL strings on purpose — the Impact Analysis
Agent in db-change-agent does a static grep/AST pass over these files to
build a table.column -> service dependency graph, so keeping the SQL
literal (not hidden behind an ORM model) is what makes that analysis real.
"""

import psycopg2


def get_conn():
    return psycopg2.connect(dsn="postgresql://...")  # Supabase connection string, injected via env


def place_order(user_id: int, product_id: int, quantity: int, total_amount: float):
    query = """
        INSERT INTO orders (user_id, product_id, quantity, total_amount, status)
        VALUES (%s, %s, %s, %s, 'placed')
        RETURNING id;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, (user_id, product_id, quantity, total_amount))
        return cur.fetchone()[0]


def mark_order_shipped(order_id: int):
    query = "UPDATE orders SET status = 'shipped' WHERE id = %s;"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, (order_id,))


def cancel_order(order_id: int):
    query = "UPDATE orders SET status = 'cancelled' WHERE id = %s;"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, (order_id,))


def get_orders_for_user(user_id: int):
    query = """
        SELECT id, product_id, quantity, status, total_amount, created_at
        FROM orders
        WHERE user_id = %s
        ORDER BY created_at DESC;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, (user_id,))
        return cur.fetchall()


def check_stock_before_order(product_id: int):
    query = """
        SELECT quantity, reorder_threshold
        FROM inventory
        WHERE product_id = %s;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, (product_id,))
        return cur.fetchone()
