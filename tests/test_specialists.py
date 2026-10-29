
from unittest.mock import MagicMock, patch

from app.agents.account_agent import account_support_tool
from app.agents.billing_agent import billing_support_tool
from app.agents.technical_agent import technical_support_tool


@patch("app.agents.account_agent.trace_llm_usage")
@patch("app.agents.account_agent.openRouter_llm")
def test_account_specialist_returns_response(mock_llm, mock_trace):
    mock_response = MagicMock()
    mock_response.content = "Try resetting your password."
    mock_response.usage_metadata = {
        "input_tokens": 10, "output_tokens": 8, "total_tokens": 18,
    }
    mock_llm.invoke.return_value = mock_response

    result = account_support_tool.invoke({"customer_message": "I cannot log in"})

    assert result == "Try resetting your password."
    mock_llm.invoke.assert_called_once()
    mock_trace.assert_called_once()


@patch("app.agents.account_agent.trace_llm_usage")
@patch("app.agents.account_agent.openRouter_llm")
def test_account_specialist_handles_list_content(mock_llm, mock_trace):
    mock_response = MagicMock()
    mock_response.content = [
        {"type": "text", "text": "First instruction."},
        {"type": "text", "text": "Second instruction."},
    ]
    mock_response.usage_metadata = {}
    mock_llm.invoke.return_value = mock_response

    result = account_support_tool.invoke({"customer_message": "I need account help"})

    assert result == "First instruction.\nSecond instruction."
    mock_trace.assert_called_once()


@patch("app.agents.account_agent.trace_llm_usage")
@patch("app.agents.account_agent.openRouter_llm")
def test_account_specialist_traces_and_reraises_error(mock_llm, mock_trace):
    mock_llm.invoke.side_effect = RuntimeError("Simulated LLM failure")

    try:
        account_support_tool.invoke({"customer_message": "I cannot log in"})
        assert False, "Expected RuntimeError was not raised"
    except RuntimeError as error:
        assert str(error) == "Simulated LLM failure"

    assert mock_trace.call_count == 1
    assert mock_trace.call_args.kwargs["error"] is not None


@patch("app.agents.billing_agent.is_billing_support_enabled", return_value=True)
@patch("app.agents.billing_agent.trace_llm_usage")
@patch("app.agents.billing_agent.gemini_llm")
@patch("app.agents.billing_agent.find_customer_transactions", return_value=[])
def test_billing_specialist_returns_response(mock_find_transactions, mock_llm, mock_trace, mock_kill_switch):
    mock_response = MagicMock()
    mock_response.content = "Review your invoice for the duplicate charge."
    mock_response.usage_metadata = {
        "input_tokens": 10, "output_tokens": 8, "total_tokens": 18,
    }
    mock_llm.invoke.return_value = mock_response

    result = billing_support_tool.invoke({
        "customer_message": (
            "I was charged twice. My account email is customer@example.com. "
            "The transaction was on October 20 for $50."
        )
    })

    assert result == "Review your invoice for the duplicate charge."
    mock_llm.invoke.assert_called_once()
    mock_trace.assert_called_once()


@patch("app.agents.billing_agent.is_billing_support_enabled", return_value=True)
@patch("app.agents.billing_agent.trace_llm_usage")
@patch("app.agents.billing_agent.gemini_llm")
@patch("app.agents.billing_agent.find_customer_transactions", return_value=[])
def test_billing_specialist_does_not_claim_refund_was_processed(
    mock_find_transactions,
    mock_llm,
    mock_trace,
    mock_kill_switch,
):
    mock_response = MagicMock()
    mock_response.content = (
        "I cannot confirm that a refund has been issued. "
        "Please check with billing support."
    )
    mock_response.usage_metadata = {}
    mock_llm.invoke.return_value = mock_response

    result = billing_support_tool.invoke({
        "customer_message": (
            "Has my refund been issued? My account email is customer@example.com. "
            "The transaction was on October 20 for $50."
        )
    })

    assert "cannot confirm" in result.lower()
    assert "refund" in result.lower()
    mock_trace.assert_called_once()


@patch("app.agents.technical_agent.trace_llm_usage")
@patch("app.agents.technical_agent.openRouter_llm_google")
def test_technical_specialist_returns_response(mock_llm, mock_trace):
    mock_response = MagicMock()
    mock_response.content = "Restart the application and check for updates."
    mock_response.usage_metadata = {
        "input_tokens": 10, "output_tokens": 8, "total_tokens": 18,
    }
    mock_llm.invoke.return_value = mock_response

    result = technical_support_tool.invoke(
        {"customer_message": "My application crashes"}
    )

    assert result == "Restart the application and check for updates."
    mock_llm.invoke.assert_called_once()
    mock_trace.assert_called_once()


@patch("app.agents.technical_agent.trace_llm_usage")
@patch("app.agents.technical_agent.openRouter_llm_google")
def test_technical_specialist_does_not_claim_unverified_repair(
    mock_llm, mock_trace,
):
    mock_response = MagicMock()
    mock_response.content = (
        "I cannot directly access or repair your system. "
        "Please restart the application and share any error message."
    )
    mock_response.usage_metadata = {}
    mock_llm.invoke.return_value = mock_response

    result = technical_support_tool.invoke(
        {"customer_message": "Can you fix my application?"}
    )

    assert "cannot directly access or repair" in result.lower()
    mock_trace.assert_called_once()


@patch("app.agents.technical_agent.trace_llm_usage")
@patch("app.agents.technical_agent.openRouter_llm_google")
def test_technical_specialist_traces_and_reraises_error(mock_llm, mock_trace):
    mock_llm.invoke.side_effect = RuntimeError("Simulated technical failure")

    try:
        technical_support_tool.invoke(
            {"customer_message": "My application crashes"}
        )
        assert False, "Expected RuntimeError was not raised"
    except RuntimeError as error:
        assert str(error) == "Simulated technical failure"

    assert mock_trace.call_count == 1
    assert mock_trace.call_args.kwargs["error"] is not None
