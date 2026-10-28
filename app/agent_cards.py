import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENT_CARDS_DIR = PROJECT_ROOT / "agent_cards"


def load_agent_card(agent_id: str) -> dict[str, Any]:
    """Load and validate the basic structure of an agent card."""
    card_path = AGENT_CARDS_DIR / f"{agent_id}.json"

    # Prevent loading files outside the agent_cards directory.
    if card_path.parent != AGENT_CARDS_DIR:
        raise ValueError("Invalid agent ID.")

    if not card_path.is_file():
        raise FileNotFoundError(f"Agent card not found: {agent_id}")

    with card_path.open("r", encoding="utf-8") as file:
        card = json.load(file)

    required_fields = {
        "agent_id",
        "name",
        "description",
        "version",
        "agent_type",
        "capabilities",
        "available_tools",
        "permissions",
        "status",
    }

    missing_fields = required_fields - card.keys()
    if missing_fields:
        raise ValueError(
            f"Agent card '{agent_id}' is missing fields: "
            f"{', '.join(sorted(missing_fields))}"
        )

    if card["agent_id"] != agent_id:
        raise ValueError(
            f"Agent ID mismatch in card: expected '{agent_id}'."
        )

    return card


def load_all_agent_cards() -> dict[str, dict[str, Any]]:
    """Load all registered agent cards."""
    agent_ids = (
        "supervisor",
        "account_support",
        "billing_support",
        "technical_support",
    )

    return {
        agent_id: load_agent_card(agent_id)
        for agent_id in agent_ids
    }