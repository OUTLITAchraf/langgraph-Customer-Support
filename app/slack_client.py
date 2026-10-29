import json
import logging
import os

from typing import Set
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import threading

from app.incident_workflow import (
    resume_incident_workflow,
    run_incident_workflow,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()

slack_app = App(
    token=os.getenv("SLACK_BOT_TOKEN", "xoxb-test-token"),
    token_verification_enabled=False,
)
CHANNEL_ID = os.environ["SLACK_APPROVAL_CHANNEL_ID"]
APPROVER_USER_IDS: Set[str] = {
    user_id.strip()
    for user_id in os.getenv("SLACK_APPROVER_USER_IDS", "").split(",")
    if user_id.strip()
}

processed_incidents: set[str] = set()
processing_lock = threading.Lock()


def send_incident_for_approval(incident: dict, thread_id: str) -> None:
    """Start the incident workflow and post its approval request to Slack."""
    result = run_incident_workflow(incident, thread_id)

    # LangGraph returns __interrupt__ when it pauses for approval.
    if "__interrupt__" not in result:
        logger.info("Incident workflow did not pause: %s", incident["incident_id"])
        return

    incident_id = incident["incident_id"]
    action_data = {
        "incident_id": incident_id,
        "thread_id": thread_id,
    }
    button_value = json.dumps(action_data)

    action = incident["proposed_action"]

    slack_app.client.chat_postMessage(
        channel=CHANNEL_ID,
        text=f"Approval required for incident {incident_id}",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Incident:* {incident_id}\n"
                        f"*Severity:* {incident['severity']}\n"
                        f"*Affected agent:* {incident['affected_agent']}\n"
                        f"*Description:* {incident['description']}\n"
                        f"*Proposed action:* {action['description']}\n"
                        f"*Reason:* {action['reason']}\n"
                        f"*Expected impact:* {action['expected_impact']}"
                    ),
                },
            },
            {
                "type": "actions",
                "block_id": f"approval_{incident_id}",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Approve",
                        },
                        "style": "primary",
                        "action_id": "approve_incident",
                        "value": button_value,
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Reject",
                        },
                        "style": "danger",
                        "action_id": "reject_incident",
                        "value": button_value,
                    },
                ],
            },
        ],
    )

    logger.info("Approval request posted for incident %s", incident_id)


def process_decision(body: dict, decision: str) -> None:
    """Resume the paused workflow with the selected decision."""
    action = body["actions"][0]
    data = json.loads(action["value"])

    incident_id = data["incident_id"]
    thread_id = data["thread_id"]
    user_id = body["user"]["id"]

    if not APPROVER_USER_IDS:
        raise PermissionError(
            "No authorized approvers configured in SLACK_APPROVER_USER_IDS."
        )

    if user_id not in APPROVER_USER_IDS:
        raise PermissionError(
            f"Slack user {user_id} is not authorized to approve incidents."
        )

    with processing_lock:
        if incident_id in processed_incidents:
            raise ValueError(
                f"Incident {incident_id} already has a submitted decision."
            )

        processed_incidents.add(incident_id)


    try:
        result = resume_incident_workflow(
            thread_id,
            {
                "decision": decision,
                "approved_by": user_id,
            },
        )
    except Exception:
        with processing_lock:
            processed_incidents.discard(incident_id)
        raise

    logger.info(
        "Incident %s decision=%s user=%s result=%s",
        incident_id,
        decision,
        user_id,
        result.get("execution_result", "No execution result returned"),
    )

    slack_app.client.chat_postMessage(
        channel=CHANNEL_ID,
        text=(
            f"Incident {incident_id}: decision *{decision.upper()}* "
            f"recorded from Slack user `{user_id}`."
        ),
    )


@slack_app.action("approve_incident")
def handle_approval(ack, body, logger):
    ack()
    try:
        process_decision(body, "approve")
    except Exception:
        logger.exception("Failed to process incident approval")


@slack_app.action("reject_incident")
def handle_rejection(ack, body, logger):
    ack()
    try:
        process_decision(body, "reject")
    except Exception:
        logger.exception("Failed to process incident rejection")


def start_slack_app():
    logger.info("Starting Slack Socket Mode connection...")
    handler = SocketModeHandler(
        slack_app,
        os.environ["SLACK_APP_TOKEN"],
    )
    handler.start()


if __name__ == "__main__":
    start_slack_app()
