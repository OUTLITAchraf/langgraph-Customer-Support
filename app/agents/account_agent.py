import time

from langchain_core.tools import tool

from app.llm import gemini_llm
from app.observability.tracing import trace_llm_usage


@tool
def account_support_tool(customer_message: str) -> str:
    """Handle login, password, and account-access issues."""

    prompt = [
        (
            "system",
            """
            You are an account support specialist.

            Help customers with login problems, forgotten passwords,
            and account access.

            Give clear, safe troubleshooting advice.
            Never ask for passwords or authentication codes.
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
            name="account-support-agent",
            input_data={"customer_message": customer_message},
            output_data={"response": final_response},
            usage=usage,
            metadata={
                "agent": "account_support",
                "project": "customer-support-platform",
                "latency_ms": latency_ms,
                "provider": "gemini",
            },
        )

        return final_response

    except Exception as error:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        trace_llm_usage(
            name="account-support-agent",
            input_data={"customer_message": customer_message},
            output_data={},
            metadata={
                "agent": "account_support",
                "project": "customer-support-platform",
                "latency_ms": latency_ms,
                "provider": "gemini",
            },
            error=error,
        )

        raise