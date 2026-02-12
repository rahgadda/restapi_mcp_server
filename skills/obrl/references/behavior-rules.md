## Behavior Rules

1. Steps must be validated in sequence (1 → 40).
2. If a step fails or a required input/state is missing, the agent must stop further execution immediately. Do not ask the user for input; execute steps strictly based on user-provided inputs.
3. The user can request to start from any step, but all previous steps must still be verified.
4. The agent must reuse already validated steps whenever possible.
5. MCP name is always: `restapi-mcp-server`.
7. Stop execution if any skill fails to execute.
8. Do not ask for user input for continuation; execute steps based on user input.
9. Do not create or include any request/response payload fields, headers, or post_script variables that are not explicitly present in this SKILL.md. Use the provided payload templates exactly as written.
10. Do not synthesize, derive, or upsert environment variables that are not explicitly named in this SKILL.md. If any required variable is missing, stop execution with a clear failure.
11. Do not add extra API calls, intermediate payloads, or additional keys to request_body, request_headers, or post_script beyond those shown for each step in this SKILL.md.
12. If a referenced placeholder variable is missing at runtime, stop execution rather than inferring or inventing a value.