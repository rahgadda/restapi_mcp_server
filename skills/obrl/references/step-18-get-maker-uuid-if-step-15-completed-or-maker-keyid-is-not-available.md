### Step 18 — GET-MAKER-UUID (If Step 16 completed OR MAKER-KEYID is not available)
- Execution Condition:
  - Execute if Step 16 is done OR `MAKER-KEYID` is not available in environment.
- Do not replace any json payload values.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "GET",
    "action": "GET-MAKER-UUID",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{SMS-CORE-SERVICES}}/user?includecloseandunauth=true&offset=0&limit=10&userLoginId={{MAKER-ID}}",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{MAKER-ID}}",
      "branchCode": "{{DEFAULT-BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY",
      "appId": "sms",
      "authtoken": "y"
    },
    "post_script": {
      "{{MAKER-KEYID}}": "jq_expression('.data[0].keyId', $RESPONSE_BODY)"
    }
  }
  ```
- Success Condition:
  - `MAKER-KEYID` stored in env store.

