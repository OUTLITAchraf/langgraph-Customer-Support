from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.workflow import run_support_workflow

app = FastAPI(
    title="Customer Support Intelligence Platform",
    description="Multi-agent customer support with Agent Observability",
    version="0.1.0",
)


class SupportRequest(BaseModel):
    customer_message: str


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

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your support request.",
        )