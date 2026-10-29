from app.agents.billing_agent import billing_support_tool
from unittest.mock import patch

def test_billing_agent_asks_for_missing_email():
    with patch(
        "app.agents.billing_agent.is_billing_support_enabled",
        return_value=True,
    ):
        response = billing_support_tool.invoke({
            "customer_message": "I was charged twice. Can you help?"
        })

    assert isinstance(response, str)
    assert response.strip()
    assert "email" in response.lower() or "account" in response.lower()