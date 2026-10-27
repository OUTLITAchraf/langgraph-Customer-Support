from app.observability.langfuse_client import langfuse


def trace_operation(
    name: str,
    input_data: dict,
    output_data: dict,
    metadata: dict | None = None,
    error: Exception | None = None,
) -> None:
    """Record an operation and capture errors in Langfuse."""

    with langfuse.start_as_current_observation(
        as_type="span",
        name=name,
    ) as span:
        span.update(
            input=input_data,
            output=output_data,
            metadata=metadata or {},
        )

        if error is not None:
            span.update(
                level="ERROR",
                status_message=str(error),
            )

    langfuse.flush()


def trace_llm_usage(
    name: str,
    input_data: dict,
    output_data: dict,
    usage: dict | None = None,
    metadata: dict | None = None,
    error: Exception | None = None,
) -> None:
    """Record an LLM generation, token usage, latency, and errors."""

    with langfuse.start_as_current_observation(
        as_type="generation",
        name=name,
    ) as generation:
        generation.update(
            input=input_data,
            output=output_data,
            metadata=metadata or {},
        )

        if usage:
            generation.update(
                usage_details={
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }
            )

        if error is not None:
            generation.update(
                level="ERROR",
                status_message=str(error),
            )

    langfuse.flush()