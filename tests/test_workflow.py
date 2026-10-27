
from unittest.mock import MagicMock, patch

from app.workflow import run_support_workflow


@patch("app.workflow.langfuse.flush")
@patch("app.workflow.support_graph.invoke")
@patch("app.workflow.langfuse.start_as_current_observation")
def test_workflow_returns_final_response(
    mock_observation,
    mock_graph_invoke,
    mock_flush,
):
    mock_span = MagicMock()
    mock_observation.return_value.__enter__.return_value = mock_span

    expected_response = "Your account support request has been processed."

    mock_graph_invoke.return_value = {
        "customer_message": "I cannot log in",
        "category": "account_access",
        "analysis": "",
        "final_response": expected_response,
    }

    result = run_support_workflow("I cannot log in")

    assert result == expected_response

    mock_observation.assert_called_once_with(
        as_type="span",
        name="customer-support-workflow",
    )

    mock_graph_invoke.assert_called_once_with({
        "customer_message": "I cannot log in",
        "category": "",
        "analysis": "",
        "final_response": "",
    })

    mock_span.update.assert_any_call(
        input={"customer_message": "I cannot log in"},
        metadata={
            "project": "customer-support-platform",
            "workflow": "langgraph",
        },
    )

    mock_span.update.assert_any_call(
        output={"final_response": expected_response}
    )

    mock_flush.assert_called_once()
