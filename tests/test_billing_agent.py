from app.agents.billing_agent import billing_support_tool


def test_billing_agent_asks_for_missing_email():
    response = billing_support_tool.invoke({
        "customer_message": "I was charged twice. Can you help?"
    })

    assert isinstance(response, str)
    assert response.strip()
    assert "email" in response.lower() or "account" in response.lower()