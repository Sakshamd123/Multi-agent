"""
refunds-service: processes refund requests against existing orders.
Note the read of orders.total_amount below -- this is a deliberate real
cross-service dependency: a schema change to orders.total_amount (e.g.
type change, NOT NULL added, column renamed) should be flagged by the
Impact Analysis Agent as affecting refunds-service too.
"""

import psycopg2


def get_conn():
    return psycopg2.connect(dsn="postgresql://...")


def request_refund(order_id: int, user_id: int, amount: float, reason: str):
    validate_query = """
        SELECT total_amount, status
        FROM orders
        WHERE id = %s AND user_id = %s;
    """
    insert_query = """
        INSERT INTO refunds (order_id, user_id, amount, reason, status)
        VALUES (%s, %s, %s, %s, 'pending')
        RETURNING id;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(validate_query, (order_id, user_id))
        order = cur.fetchone()
        if order is None or amount > order[0]:
            raise ValueError("refund amount exceeds order total")
        cur.execute(insert_query, (order_id, user_id, amount, reason))
        return cur.fetchone()[0]


def approve_refund(refund_id: int):
    query = "UPDATE refunds SET status = 'approved' WHERE id = %s;"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, (refund_id,))


def reject_refund(refund_id: int):
    query = "UPDATE refunds SET status = 'rejected' WHERE id = %s;"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, (refund_id,))


def get_refunds_for_order(order_id: int):
    query = """
        SELECT id, amount, reason, status, created_at
        FROM refunds
        WHERE order_id = %s;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, (order_id,))
        return cur.fetchall()
