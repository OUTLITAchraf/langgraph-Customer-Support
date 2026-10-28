
# INC-004: Langfuse Observability Unavailable

## Incident Details
- **Incident ID:** INC-004
- **Severity:** Medium
- **Affected Component:** Langfuse tracing and observability
- **Status:** Operational procedure

## Symptoms
- Workflow traces are missing from Langfuse.
- Trace initialization or export produces an error.
- Observability data is delayed or incomplete.
- The application reports a tracing connection failure.

## Investigation
1. Check whether Langfuse is reachable.
2. Verify the configured Langfuse host.
3. Confirm that the public and secret keys are configured correctly.
4. Inspect application logs for tracing initialization or export errors.
5. Determine whether the support workflow itself is failing or only tracing.

## Recovery Procedure
1. Correct invalid host or credential configuration.
2. Check Langfuse service availability.
3. Restart or retry tracing initialization only if appropriate.
4. Preserve application error logs while avoiding exposure of secrets.
5. Do not disable essential application error handling just to restore tracing.

## Verification
1. Submit a test customer request.
2. Confirm that the support workflow completes.
3. Check that a new trace appears in Langfuse.
4. Verify that workflow metadata and relevant error details are recorded.

## Escalation
Escalate to the platform maintainer if traces remain unavailable after configuration and service checks.

## Closure Criteria
Langfuse receives new traces, and the support workflow behaves as expected.
