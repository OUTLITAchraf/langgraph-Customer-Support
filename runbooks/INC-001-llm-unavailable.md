
# INC-001: LLM Provider Unavailable

## Incident Details
- **Incident ID:** INC-001
- **Severity:** High
- **Affected Component:** LLM provider and supervisor workflow
- **Status:** Operational procedure

## Symptoms
- Customer requests fail during processing.
- The API returns HTTP 500.
- Langfuse records a failed workflow or LLM operation.
- The LLM provider returns a timeout, connection error, or service error.

## Investigation
1. Open the failed request in Langfuse.
2. Identify the operation that failed and inspect its error message.
3. Check the configured LLM provider's service status.
4. Verify that the API key and model configuration are valid.
5. Check whether the failure is temporary or persistent.

## Recovery Procedure
1. Confirm the provider's availability.
2. Correct invalid configuration if necessary.
3. If a provider outage is confirmed, use an approved fallback provider if one is configured and tested.
4. Retry the request after confirming that the cause has been addressed.
5. Do not expose API keys or secrets in logs.

## Verification
1. Submit a test customer request.
2. Confirm that the workflow returns a response.
3. Verify that Langfuse records a successful trace.

## Escalation
Escalate to the platform maintainer if the provider remains unavailable or repeated requests continue to fail.

## Closure Criteria
The provider is responding, customer requests succeed, and the incident is documented.
