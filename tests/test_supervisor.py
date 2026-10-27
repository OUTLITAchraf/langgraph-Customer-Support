
from unittest.mock import MagicMock, patch

from app.agents.supervisor import supervisor_agent


@patch("app.agents.supervisor.trace_llm_usage")
@patch("app.agents.supervisor.supervisor_llm")
@patch("app.agents.supervisor.specialist_tools")
def test_supervisor_routes_account_request(
    mock_tools, mock_supervisor_llm, mock_trace,
):
    mock_response = MagicMock()
    mock_response.tool_calls = [
        {
            "name": "account_support_tool",
            "args": {"customer_message": "I cannot log in"},
        }
    ]
    mock_response.content = ""
    mock_response.usage_metadata = {
        "input_tokens": 10, "output_tokens": 5, "total_tokens": 15,
    }
    mock_supervisor_llm.invoke.return_value = mock_response

    mock_account_tool = MagicMock()
    mock_account_tool.name = "account_support_tool"
    mock_account_tool.invoke.return_value = "Account support response"
    mock_tools.__iter__.return_value = iter([mock_account_tool])

    result = supervisor_agent("I cannot log in")

    assert result == "Account support response"
    mock_supervisor_llm.invoke.assert_called_once()
    mock_account_tool.invoke.assert_called_once_with(
        {"customer_message": "I cannot log in"}
    )
    mock_trace.assert_called_once()
