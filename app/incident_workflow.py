from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver

from app.incidents import Incident


class IncidentState(TypedDict):
    incident: Incident
    execution_result: str


def request_human_approval(state: IncidentState) -> dict:
    incident = state["incident"]

    # Pause execution until a human submits an approval decision.
    decision = interrupt({
        "incident_id": incident["incident_id"],
        "severity": incident["severity"],
        "description": incident["description"],
        "proposed_action": incident["proposed_action"],
        "message": "Approve or reject this recovery action.",
    })

    if not isinstance(decision, dict):
        raise ValueError("Approval decision must be an object.")

    if decision.get("decision") not in {"approve", "reject"}:
        raise ValueError("Decision must be 'approve' or 'reject'.")

    updated_incident = dict(incident)

    if decision["decision"] == "reject":
        updated_incident["status"] = "rejected"
        updated_incident["approval_decision"] = "rejected"
        return {
            "incident": updated_incident,
            "execution_result": "Recovery action rejected; nothing executed.",
        }

    updated_incident["status"] = "approved"
    updated_incident["approval_decision"] = "approved"
    updated_incident["approved_by"] = str(
        decision.get("approved_by", "unspecified")
    )

    return {"incident": updated_incident}


def execute_approved_action(state: IncidentState) -> dict:
    incident = state["incident"]

    # Defense in depth: never execute an unapproved action.
    if incident["approval_decision"] != "approved":
        raise PermissionError("Recovery action has not been approved.")

    # Placeholder only. Real recovery handlers will be added separately.
    return {
        "execution_result": (
            f"Approval confirmed for incident {incident['incident_id']}. "
            "No recovery action is configured yet."
        )
    }


def route_after_approval(state: IncidentState) -> str:
    if state["incident"]["approval_decision"] == "approved":
        return "execute"
    return "finish"


builder = StateGraph(IncidentState)

builder.add_node("approval", request_human_approval)
builder.add_node("execute", execute_approved_action)

builder.add_edge(START, "approval")
builder.add_conditional_edges(
    "approval",
    route_after_approval,
    {
        "execute": "execute",
        "finish": END,
    },
)
builder.add_edge("execute", END)

incident_graph = builder.compile(checkpointer=MemorySaver())


def run_incident_workflow(incident: Incident, thread_id: str):
    return incident_graph.invoke(
        {
            "incident": incident,
            "execution_result": "",
        },
        config={"configurable": {"thread_id": thread_id}},
    )


def resume_incident_workflow(thread_id: str, decision: dict):
    return incident_graph.invoke(
        Command(resume=decision),
        config={"configurable": {"thread_id": thread_id}},
    )