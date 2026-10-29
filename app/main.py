import os
import secrets

from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

from app.workflow import run_support_workflow
from app.governance.kill_switch import (
    is_billing_support_enabled,
    set_billing_support_enabled,
)

load_dotenv()
security = HTTPBearer(auto_error=False)

app = FastAPI(
    title="Customer Support Intelligence Platform",
    description="Multi-agent customer support with Agent Observability",
    version="0.1.0",
)


class SupportRequest(BaseModel):
    customer_message: str


class KillSwitchRequest(BaseModel):
    enabled: bool


def verify_admin_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> None:
    expected_token = os.getenv("BILLING_KILL_SWITCH_TOKEN")

    if not expected_token:
        raise HTTPException(
            status_code=503,
            detail="Kill-switch authorization is not configured.",
        )

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Administrator authorization required.",
        )

    supplied_token = credentials.credentials

    if not secrets.compare_digest(supplied_token, expected_token):
        raise HTTPException(
            status_code=403,
            detail="Invalid administrator token.",
        )


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "customer-support-platform",
    }


@app.post("/support")
def handle_support_request(request: SupportRequest):
    message = request.customer_message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Customer message cannot be empty.",
        )

    try:
        response = run_support_workflow(message)

        return {
            "customer_message": message,
            "response": response,
        }

    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your support request.",
        )


@app.get("/admin/billing-kill-switch")
def billing_kill_switch_status(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    verify_admin_token(credentials)

    return {
        "agent": "billing_support",
        "enabled": is_billing_support_enabled(),
    }


@app.put("/admin/billing-kill-switch")
def update_billing_kill_switch(
    request: KillSwitchRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    verify_admin_token(credentials)

    enabled = set_billing_support_enabled(request.enabled)

    return {
        "agent": "billing_support",
        "enabled": enabled,
        "message": (
            "Billing support enabled."
            if enabled
            else "Billing support disabled."
        ),
    }


@app.post("/admin/billing-kill-switch/disable")
def disable_billing_support(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    verify_admin_token(credentials)

    set_billing_support_enabled(False)

    return {
        "agent": "billing_support",
        "enabled": False,
        "message": "Billing support disabled.",
    }