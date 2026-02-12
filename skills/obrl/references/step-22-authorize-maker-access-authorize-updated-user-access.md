### Step 22 — AUTHORIZE-MAKER-ACCESS (Authorize updated user access)
- Do not replace any json payload values.
- Execution Condition:
  - Execute only after Step 22 successfully completed (Maker access updated) and when `MAKER-KEYID`, `MAKER-MODE-NEXT`, and `TEMP-CHECKER-ID` are available.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "PATCH",
    "action": "AUTHORIZE-MAKER-ACCESS",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{SMS-CORE-SERVICES}}/user/{{MAKER-KEYID}}/approve",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{TEMP-CHECKER-ID}}",
      "branchCode": "{{DEFAULT-BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY",
      "appId": "sms",
      "authtoken": "y"
    },
    "request_body": {
      "id": "{{MAKER-KEYID}}",
      "modNos": ["{{MAKER-MODE-NEXT}}"],
      "remarks": "Approved"
    }
  }
  ```
- Success Condition:
  - Maker access update authorized.

