from typing import Literal, TypedDict
from datetime import datetime, timezone
from uuid import uuid4


IncidentSeverity = Literal["low", "medium", "high", "critical"]

IncidentStatus = Literal[
    "detected",
    "awaiting_approval",
    "approved",
    "rejected",
    "executing",
    "resolved",
    "failed",
]


class RecoveryAction(TypedDict):
    action_id: str
    description: str
    reason: str
    expected_impact: str


class Incident(TypedDict):
    incident_id: str
    incident_type: str
    severity: IncidentSeverity
    affected_agent: str
    description: str
    status: IncidentStatus
    proposed_action: RecoveryAction
    approval_decision: Literal["pending", "approved", "rejected"]
    approved_by: str | None
    created_at: str


def create_incident(
    incident_type: str,
    severity: IncidentSeverity,
    affected_agent: str,
    description: str,
    action_description: str,
    action_reason: str,
    expected_impact: str,
) -> Incident:
    """Create an incident with a proposed recovery action awaiting approval."""

    return {
        "incident_id": str(uuid4()),
        "incident_type": incident_type,
        "severity": severity,
        "affected_agent": affected_agent,
        "description": description,
        "status": "awaiting_approval",
        "proposed_action": {
            "action_id": str(uuid4()),
            "description": action_description,
            "reason": action_reason,
            "expected_impact": expected_impact,
        },
        "approval_decision": "pending",
        "approved_by": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }