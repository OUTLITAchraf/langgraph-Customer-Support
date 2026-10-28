
# INC-002: Specialist Agent Failure

## Incident Details
- **Incident ID:** INC-002
- **Severity:** High
- **Affected Component:** Account, billing, or technical support specialist
- **Status:** Operational procedure

## Symptoms
- A specialist tool raises an exception.
- The supervisor selects a tool, but no valid response is returned.
- Customer requests fail or return incomplete responses.
- Langfuse records an error during specialist execution.

## Investigation
1. Open the failed workflow trace in Langfuse.
2. Identify which specialist was selected.
3. Inspect the specialist operation's input and error details.
4. Check the specialist's implementation and LLM configuration.
5. Verify that the tool name and expected input structure match.

## Recovery Procedure
1. Correct the identified implementation or configuration issue.
2. Confirm that the specialist returns a valid response.
3. If a retry mechanism already exists, use it according to its configured limits.
4. Avoid repeatedly retrying permanent errors.
5. Do not claim that a request was resolved if the specialist failed.

## Verification
1. Submit a test request for the affected category.
2. Confirm that the supervisor selects the expected specialist.
3. Verify that a valid response is returned.
4. Check the corresponding Langfuse trace.

## Escalation
Escalate to the developer responsible for the affected specialist if the failure persists.

## Closure Criteria
The specialist completes the request successfully and the failure is documented.
