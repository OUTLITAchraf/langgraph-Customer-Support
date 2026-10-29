import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def find_customer_transactions(
    customer_email: str,
    start_date=None,
    end_date=None,
    amount=None,
) -> list[dict]:
    """Find a customer's transactions by email, date range, and amount."""

    database_url = os.getenv("SUPABASE_DATABASE_URL")

    if not database_url:
        raise RuntimeError("SUPABASE_DATABASE_URL is not configured.")

    query = """
        SELECT
            transaction_reference,
            amount,
            currency,
            transaction_date,
            status,
            description
        FROM public.transactions
        WHERE LOWER(customer_email) = LOWER(%s)
    """

    params = [customer_email.strip()]

    if start_date is not None:
        query += " AND transaction_date >= %s"
        params.append(start_date)

    if end_date is not None:
        query += " AND transaction_date < %s"
        params.append(end_date)

    if amount is not None:
        query += " AND amount = %s"
        params.append(amount)

    query += " ORDER BY transaction_date DESC"

    with psycopg.connect(database_url, connect_timeout=10) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            columns = [column.name for column in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]