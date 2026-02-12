### Step 10 — Populate MAKER-TOKEN
- Do not replace any json payload values.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "POST",
    "action": "CREATE-MAKER-USER-TOKEN",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{API-GATEWAY}}/platojwtauth/",
    "request_headers": {
      "Content-Type": "application/json",
      "appId": "sms"
    },
    "request_body": {
      "username": "base64_encode({{MAKER-ID}})",
      "password": "base64_encode(welcome1)"
    },
    "post_script": {
      "{{MAKER-TOKEN}}": "jq_expression('.token', $RESPONSE_BODY)"
    }
  }
  ```
- Success Condition:
  - `MAKER-TOKEN` stored in env store.

