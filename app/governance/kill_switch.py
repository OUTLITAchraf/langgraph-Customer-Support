import os

import psycopg2


def get_db_connection():
    database_url = os.getenv("SUPABASE_DATABASE_URL")

    if not database_url:
        raise RuntimeError("SUPABASE_DATABASE_URL is not configured.")

    return psycopg2.connect(database_url)


def is_billing_support_enabled() -> bool:
    """Read the shared billing kill-switch state from PostgreSQL."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT enabled
                FROM public.agent_kill_switches
                WHERE agent_name = %s
                """,
                ("billing_support",),
            )
            row = cur.fetchone()

    if row is None:
        raise RuntimeError("Billing kill-switch state is missing.")

    return row[0]


def set_billing_support_enabled(enabled: bool) -> bool:
    """Update the shared billing kill-switch state in PostgreSQL."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.agent_kill_switches
                    (agent_name, enabled, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (agent_name)
                DO UPDATE SET
                    enabled = EXCLUDED.enabled,
                    updated_at = NOW()
                RETURNING enabled
                """,
                ("billing_support", enabled),
            )
            row = cur.fetchone()

    return row[0]