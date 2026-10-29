from unittest.mock import patch

from app.agents.billing_agent import billing_support_tool


def test_billing_disabled_blocks_investigation():
    with patch(
        "app.agents.billing_agent.is_billing_support_enabled",
        return_value=False,
    ):
        result = billing_support_tool.invoke({
            "customer_message": "I was charged twice."
        })

    assert "temporarily unavailable" in result.lower()
    assert "no billing investigation was performed" in result.lower()