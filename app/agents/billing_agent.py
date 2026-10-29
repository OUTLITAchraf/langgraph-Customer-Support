import re
import time
from decimal import Decimal

from langchain_core.tools import tool

from app.llm import gemini_llm
from app.observability.tracing import trace_llm_usage
from db.transactions import find_customer_transactions
from datetime import datetime, timedelta


def extract_email(message: str) -> str | None:
    """Extract an email address from the customer's message."""
    match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        message,
    )
    return match.group(0).lower() if match else None


def extract_amount(message: str) -> Decimal | None:
    """Extract a monetary amount from a customer message."""
    match = re.search(
        r"(?<!\w)(?:USD\s*)?\$?\s*(\d+(?:,\d{3})*(?:\.\d{1,2})?)"
        r"\s*(?:USD|dollars?)?(?!\w)",
        message,
        re.IGNORECASE,
    )

    if not match:
        return None

    try:
        return Decimal(match.group(1).replace(",", ""))
    except Exception:
        return None


def extract_date_range(message: str):
    """Extract a date and return a start/end range for that day."""
    patterns = [
        r"\b(\d{4}-\d{2}-\d{2})\b",
        r"\b([A-Za-z]+ \d{1,2},? \d{4})\b",
        r"\b(\d{1,2} [A-Za-z]+ \d{4})\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, message)

        if not match:
            continue

        date_text = match.group(1).replace(",", "")

        for date_format in ("%Y-%m-%d", "%B %d %Y", "%d %B %Y"):
            try:
                parsed_date = datetime.strptime(date_text, date_format).date()
                return parsed_date, parsed_date + timedelta(days=1)
            except ValueError:
                continue

    return None, None


def format_transactions(transactions: list[dict]) -> str:
    """Show only the transaction date and amount."""
    if not transactions:
        return "No matching transactions were found in the available records."

    lines = []

    for transaction in transactions:
        date = transaction["transaction_date"]

        if hasattr(date, "strftime"):
            date = date.strftime("%Y-%m-%d")

        amount = transaction["amount"]

        if isinstance(amount, Decimal):
            amount = f"{amount:.2f}"

        lines.append(f"Date: {date}; " f"Amount: {amount} {transaction['currency']}")

    return "\n".join(lines)


def fallback_response(
    transactions: list[dict],
    customer_email: str,
) -> str:
    """Provide a privacy-conscious response when the LLM is unavailable."""

    if not transactions:
        return (
            f"Account email: {customer_email}\n"
            "I couldn't verify the reported charge using the available "
            "transaction records. Please contact a human billing "
            "specialist for review. No refund or payment change has been made."
        )

    transaction_details = format_transactions(transactions)

    if len(transactions) >= 2:
        return (
            f"Account email: {customer_email}\n"
            f"{transaction_details}\n\n"
            "I found multiple transactions, but matching amounts and dates "
            "do not prove a duplicate charge. I recommend review by a human "
            "billing specialist."
        )

    return (
        f"Account email: {customer_email}\n"
        f"{transaction_details}\n\n"
        "I couldn't determine from these records alone whether the charge "
        "is incorrect. A human billing specialist can review it."
    )


@tool
def billing_support_tool(customer_message: str) -> str:
    """Investigate billing questions using verified PostgreSQL transactions."""

    start_time = time.perf_counter()
    usage = {}
    transactions = []

    try:
        # Ask for the account email before querying the database.
        customer_email = extract_email(customer_message)

        if not customer_email:
            return (
                "I can help investigate your billing concern. "
                "What email address is associated with your account? "
                "If possible, also share the approximate transaction date "
                "and the amount you were charged. "
                "Never share your full card number or CVV."
            )

        # Read transactions belonging to this customer.
        try:
            # Extract optional filters from the complete conversation.
            amount = extract_amount(customer_message)
            start_date, end_date = extract_date_range(customer_message)

            # Search by email and apply only the filters the customer supplied.
            transactions = find_customer_transactions(
                customer_email=customer_email,
                start_date=start_date,
                end_date=end_date,
                amount=amount,
            )
        except Exception as db_error:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

            trace_llm_usage(
                name="billing-support-agent",
                input_data={"customer_message": customer_message},
                output_data={
                    "response": "Database lookup failed; escalation required."
                },
                metadata={
                    "agent": "billing_support",
                    "project": "customer-support-platform",
                    "latency_ms": latency_ms,
                    "provider": "gemini",
                    "database_error_type": type(db_error).__name__,
                },
                error=db_error,
            )

            return (
                "I'm unable to access the transaction records right now. "
                "Please contact a human billing specialist for a review. "
                "No refund or payment change has been made."
            )

        # Never interpret missing records as proof that a charge did not occur.
        transaction_context = format_transactions(transactions)

        prompt = [
            (
                "system",
                """
You are a professional billing support specialist.

Use the supplied PostgreSQL transaction records as the only source
of verified transaction facts.

Investigation rules:
- Never invent transactions, dates, amounts, currencies, or statuses.
- Never reveal transaction references or descriptions.
- Show only the customer's email, transaction date, amount, and currency.
- Matching amounts and dates may indicate a possible duplicate charge,
  but they do not prove that a duplicate occurred.
- Never claim a refund, escalation, or payment change occurred unless
  the system confirms that action was completed.
- If no records match, explain that the available records could not
  verify the reported issue and recommend human billing review.
- If the customer has not provided enough information to investigate,
  ask only for the missing details needed to continue.
- Never ask for a full payment card number or CVV.
- Never reveal another customer's transaction information.

Response rules:
- Be concise, professional, and empathetic.
- Present each matching transaction on a separate line.
- Briefly explain what the records indicate.
- If multiple transactions may represent duplicate charges, explicitly
  recommend that a human billing specialist review them.
- Do not say that a case has been escalated unless it actually has.
- If the records do not establish the cause, clearly state that the
  cause remains unconfirmed.
- End with a clear next step for the customer.
        """,
            ),
            (
                "human",
                f"""
Customer email:
{customer_email}

Customer message:
{customer_message}

Verified transactions:
{transaction_context}

Write the response using this structure:

Customer email: [customer email]

Transactions:
[List each matching transaction using only its date, amount, and currency.]

Findings:
[Explain what the records show and what remains unconfirmed.]

Recommended next step:
- When a possible duplicate charge is found, recommend contacting the
  Billing Support Team for a manual review.
- Provide the team's contact information only when it is configured
  and verified by the application.
- If no verified contact information is available, show clearly labeled
  example contact details, such as:
    Team: Billing Support Team
    Email: billing-support@example.com
    Support hours: Monday-Friday, 09:00-17:00
- Clearly state that example contact details are placeholders and must
  be replaced with the organization's actual contact information.
- Never claim that the team has been contacted or that a case has been
  escalated unless the system confirms it.

Do not include transaction references, descriptions, or internal
technical details. Do not claim that a refund or escalation occurred
unless that action is confirmed.
        """,
            ),
        ]

        response = gemini_llm.invoke(prompt)

        content = response.content
        if isinstance(content, str):
            final_response = content
        elif isinstance(content, list):
            final_response = "\n".join(
                item["text"]
                for item in content
                if isinstance(item, dict)
                and item.get("type") == "text"
                and isinstance(item.get("text"), str)
            )
        else:
            final_response = str(content)

        usage_metadata = getattr(response, "usage_metadata", None) or {}
        usage = {
            "input_tokens": usage_metadata.get("input_tokens", 0),
            "output_tokens": usage_metadata.get("output_tokens", 0),
            "total_tokens": usage_metadata.get("total_tokens", 0),
        }

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        trace_llm_usage(
            name="billing-support-agent",
            input_data={"customer_message": customer_message},
            output_data={"response": final_response},
            usage=usage,
            metadata={
                "agent": "billing_support",
                "project": "customer-support-platform",
                "latency_ms": latency_ms,
                "provider": "gemini",
                "transactions_found": len(transactions),
            },
        )

        return final_response

    except Exception as error:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        trace_llm_usage(
            name="billing-support-agent",
            input_data={"customer_message": customer_message},
            output_data={"response": "LLM unavailable; using safe fallback."},
            usage=usage,
            metadata={
                "agent": "billing_support",
                "project": "customer-support-platform",
                "latency_ms": latency_ms,
                "provider": "gemini",
                "transactions_found": len(transactions),
            },
            error=error,
        )

        return fallback_response(transactions, customer_email)
