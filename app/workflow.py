from langgraph.graph import END, START, StateGraph

from app.agent_cards import load_all_agent_cards
from app.agents.supervisor import SupportState, supervisor_agent
from app.observability.langfuse_client import langfuse

WORKFLOW_VERSION = "1.0.0"


def run_supervisor(state: SupportState) -> dict:
    result = supervisor_agent(state["customer_message"])
    return {"final_response": result}


# Build the LangGraph workflow.
builder = StateGraph(SupportState)
builder.add_node("supervisor", run_supervisor)
builder.add_edge(START, "supervisor")
builder.add_edge("supervisor", END)

support_graph = builder.compile()


def run_support_workflow(customer_message: str) -> str:
    with langfuse.start_as_current_observation(
        as_type="span",
        name="customer-support-workflow",
    ) as workflow_span:

        agent_cards = load_all_agent_cards()

        workflow_span.update(
            input={"customer_message": customer_message},
            metadata={
                "project": "customer-support-platform",
                "workflow": "langgraph",
                "workflow_version": WORKFLOW_VERSION,
                "agent_versions": {
                    agent_id: card["version"]
                    for agent_id, card in agent_cards.items()
                },
            },
        )

        try:
            result = support_graph.invoke({
                "customer_message": customer_message,
                "category": "",
                "analysis": "",
                "final_response": "",
            })

            final_response = result["final_response"]

            workflow_span.update(
                output={"final_response": final_response}
            )

            return final_response

        except Exception as error:
            workflow_span.update(
                level="ERROR",
                status_message=str(error),
                output={"status": "failed"},
            )
            raise

        finally:
            langfuse.flush()