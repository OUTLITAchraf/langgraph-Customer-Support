from langchain_core.tools import tool

from app.llm import gemini_llm

import time

from langchain_core.tools import tool

from app.llm import gemini_llm
from app.observability.tracing import trace_llm_usage


@tool
def billing_support_tool(customer_message: str) -> str:
    """Handle billing questions, duplicate charges, invoices, and refunds."""

    prompt = [
        (
            "system",
            """
            You are a billing support specialist.

            Help customers understand billing issues, duplicate charges,
            invoices, and refund procedures.

            Give clear, practical guidance.
            Do not claim that a refund has been issued or a payment changed
            unless a verified system confirms that action.
            Never request full payment card details or security codes.
            """,
        ),
        ("human", customer_message),
    ]

    start_time = time.perf_counter()

    try:
        response = gemini_llm.invoke(prompt)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        content = response.content

        if isinstance(content, str):
            final_response = content
        elif isinstance(content, list):
            text_parts = [
                item["text"]
                for item in content
                if isinstance(item, dict)
                and item.get("type") == "text"
                and isinstance(item.get("text"), str)
            ]
            final_response = "\n".join(text_parts)
        else:
            final_response = str(content)

        usage_metadata = getattr(response, "usage_metadata", None) or {}

        usage = {
            "input_tokens": usage_metadata.get("input_tokens", 0),
            "output_tokens": usage_metadata.get("output_tokens", 0),
            "total_tokens": usage_metadata.get("total_tokens", 0),
        }

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
            },
        )

        return final_response

    except Exception as error:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        trace_llm_usage(
            name="billing-support-agent",
            input_data={"customer_message": customer_message},
            output_data={},
            metadata={
                "agent": "billing_support",
                "project": "customer-support-platform",
                "latency_ms": latency_ms,
                "provider": "gemini",
            },
            error=error,
        )

        raise