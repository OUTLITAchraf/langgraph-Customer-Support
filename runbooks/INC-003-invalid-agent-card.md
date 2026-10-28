
# INC-003: Invalid Agent Card

## Incident Details
- **Incident ID:** INC-003
- **Severity:** Medium
- **Affected Component:** Agent Card metadata and loader
- **Status:** Operational procedure

## Symptoms
- Loading an Agent Card raises an exception.
- A required field is missing.
- The agent ID does not match the filename.
- A JSON file contains invalid syntax.
- Agent version metadata is missing or inconsistent.

## Investigation
1. Identify the Agent Card that failed to load.
2. Open its JSON file and validate the JSON syntax.
3. Check the required fields:
   agent_id, name, description, version, agent_type,
   capabilities, available_tools, permissions, and status.
4. Verify that agent_id matches the filename.
5. Check that the version follows Semantic Versioning:
   MAJOR.MINOR.PATCH.

## Recovery Procedure
1. Correct invalid JSON syntax or missing fields.
2. Correct any mismatch between the agent ID and filename.
3. Verify that capability and tool metadata reflect the intended agent.
4. Review changes before deploying the corrected card.
5. Reload the application or card data as required.

## Verification
1. Run the Agent Card loading check.
2. Confirm that all registered cards load successfully.
3. Verify that each card reports the expected version and status.
4. Submit a test request if the application was affected.

## Escalation
Escalate to the platform maintainer if a valid card still cannot be loaded.

## Closure Criteria
All required cards load successfully and their metadata is consistent.
