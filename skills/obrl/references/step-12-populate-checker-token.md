### Step 12 — Populate CHECKER-TOKEN
- Do not replace any json payload values.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "POST",
    "action": "CREATE-CHECKER-USER-TOKEN",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{API-GATEWAY}}/platojwtauth/",
    "request_headers": {
      "Content-Type": "application/json",
      "appId": "sms"
    },
    "request_body": {
      "username": "base64_encode({{CHECKER-ID}})",
      "password": "base64_encode(welcome1)"
    },
    "post_script": {
      "{{CHECKER-TOKEN}}": "jq_expression('.token', $RESPONSE_BODY)"
    }
  }
  ```
- Success Condition:
  - `CHECKER-TOKEN` stored in env store.

