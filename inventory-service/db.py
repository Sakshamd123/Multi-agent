"""
inventory-service: owns stock levels, decremented on order placement and
restocked on approved refunds. Reads orders.quantity and orders.status,
refunds.status and refunds.order_id -- more real cross-service coupling
for the Impact Analysis Agent to detect.
"""

import psycopg2


def get_conn():
    return psycopg2.connect(dsn="postgresql://...")


def decrement_stock_for_order(order_id: int):
    order_query = "SELECT product_id, quantity, status FROM orders WHERE id = %s;"
    update_query = """
        UPDATE inventory
        SET quantity = quantity - %s, updated_at = now()
        WHERE product_id = %s;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(order_query, (order_id,))
        product_id, quantity, status = cur.fetchone()
        if status != 'placed':
            raise ValueError("order is not in placed state")
        cur.execute(update_query, (quantity, product_id))


def restock_for_refund(refund_id: int):
    refund_query = """
        SELECT r.order_id, o.product_id, o.quantity, r.status
        FROM refunds r
        JOIN orders o ON o.id = r.order_id
        WHERE r.id = %s;
    """
    update_query = """
        UPDATE inventory
        SET quantity = quantity + %s, updated_at = now()
        WHERE product_id = %s;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(refund_query, (refund_id,))
        order_id, product_id, quantity, status = cur.fetchone()
        if status != 'approved':
            raise ValueError("refund is not approved")
        cur.execute(update_query, (quantity, product_id))


def get_low_stock(warehouse_id: int):
    query = """
        SELECT product_id, quantity, reorder_threshold
        FROM inventory
        WHERE warehouse_id = %s AND quantity < reorder_threshold;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, (warehouse_id,))
        return cur.fetchall()
