### Step 23 — GET-CHECKER-UUID (If Step 16 completed OR CHECKER-KEYID is not available)
- Execution Condition:
  - Execute if Step 16 is done OR `CHECKER-KEYID` is not available in environment.
- Do not replace any json payload values.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "GET",
    "action": "GET-CHECKER-UUID",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{SMS-CORE-SERVICES}}/user?includecloseandunauth=true&offset=0&limit=10&userLoginId={{CHECKER-ID}}",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{CHECKER-ID}}",
      "branchCode": "{{DEFAULT-BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY",
      "appId": "sms",
      "authtoken": "y"
    },
    "post_script": {
      "{{CHECKER-KEYID}}": "jq_expression('.data[0].keyId', $RESPONSE_BODY)"
    }
  }
  ```
- Success Condition:
  - `CHECKER-KEYID` stored in env store.

