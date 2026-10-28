import os
import time

from slack_bolt.adapter.socket_mode import SocketModeHandler

from app.incidents import create_incident
from app.slack_client import slack_app, send_incident_for_approval

def main():

    handler = SocketModeHandler(
        slack_app,
        os.environ["SLACK_APP_TOKEN"],
    )

    handler.connect()

    incident = create_incident(
        incident_type="specialist_failure",
        severity="medium",
        affected_agent="billing_support",
        description="Test incident for Slack human approval.",
        action_description="Restart the billing specialist",
        action_reason="The specialist failed during a test request.",
        expected_impact="Billing support may become available again.",
    )

    thread_id = incident["incident_id"]

    print(f"Creating approval request for: {thread_id}")

    send_incident_for_approval(
        incident=incident,
        thread_id=thread_id,
    )

    # Keep the process alive while waiting for the Slack decision.
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()