import time
from typing import TypedDict

from app.agents.account_agent import account_support_tool
from app.agents.billing_agent import billing_support_tool
from app.agents.technical_agent import technical_support_tool
from app.llm import openRouter_llm
from app.observability.tracing import trace_llm_usage, trace_operation


class SupportState(TypedDict):
    """Shared state for the customer support workflow."""

    customer_message: str
    category: str
    analysis: str
    final_response: str


# Give the Supervisor access to the specialist tools.
specialist_tools = [
    account_support_tool,
    billing_support_tool,
    technical_support_tool,
]

# Enable the LLM to request calls to these tools.
supervisor_llm = openRouter_llm.bind_tools(specialist_tools)


def supervisor_agent(customer_message: str) -> str:
    """Select a specialist, execute its tool, and return the answer."""

    prompt = [
        (
            "system",
            """
            You are the Supervisor of a customer support platform.

            Delegate every customer request to the most appropriate tool:
            - account_support_tool: login and account access.
            - billing_support_tool: charges, invoices, and refunds.
            - technical_support_tool: application errors and crashes.

            Call the specialist tool. Do not answer the issue yourself.
            """,
        ),
        ("human", customer_message),
    ]

    start_time = time.perf_counter()

    try:
        response = supervisor_llm.invoke(prompt)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        usage_metadata = getattr(response, "usage_metadata", None) or {}

        usage = {
            "input_tokens": usage_metadata.get("input_tokens", 0),
            "output_tokens": usage_metadata.get("output_tokens", 0),
            "total_tokens": usage_metadata.get("total_tokens", 0),
        }

        trace_llm_usage(
            name="supervisor-agent",
            input_data={"customer_message": customer_message},
            output_data={
                "tool_calls": [
                    {
                        "name": call["name"],
                        "arguments": call["args"],
                    }
                    for call in response.tool_calls
                ],
                "content": str(response.content),
            },
            usage=usage,
            metadata={
                "agent": "supervisor",
                "project": "customer-support-platform",
                "latency_ms": latency_ms,
                "provider": "openRouter",
            },
        )

    except Exception as error:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        trace_operation(
            name="supervisor_error",
            input_data={"customer_message": customer_message},
            output_data={"status": "failed"},
            metadata={
                "stage": "supervisor_llm_invoke",
                "latency_ms": latency_ms,
            },
            error=error,
        )
        raise

    # Execute each specialist tool requested by the LLM.
    if response.tool_calls:
        for tool_call in response.tool_calls:
            selected_tool = next(
                (tool for tool in specialist_tools if tool.name == tool_call["name"]),
                None,
            )

            if selected_tool is None:
                continue

            try:
                result = selected_tool.invoke(tool_call["args"])

            except Exception as error:
                trace_operation(
                    name="specialist_tool_error",
                    input_data={
                        "tool_name": selected_tool.name,
                        "arguments": tool_call["args"],
                    },
                    output_data={"status": "failed"},
                    metadata={
                        "stage": "specialist_tool_execution",
                        "tool_name": selected_tool.name,
                    },
                    error=error,
                )
                raise

            return result

    return "I could not select a specialist. Please try again."
