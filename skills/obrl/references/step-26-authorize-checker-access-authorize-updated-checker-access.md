### Step 26 — AUTHORIZE-CHECKER-ACCESS (Authorize updated Checker access)
- Do not replace any json payload values.
- Execution Condition:
  - Execute only after Step 25 successfully completed (Checker access updated) and when `CHECKER-KEYID`, `CHECKER-MODE-NEXT`, and `TEMP-CHECKER-ID` are available.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "PATCH",
    "action": "AUTHORIZE-CHECKER-ACCESS",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{SMS-CORE-SERVICES}}/user/{{CHECKER-KEYID}}/approve",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{TEMP-CHECKER-ID}}",
      "branchCode": "{{DEFAULT-BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY",
      "appId": "sms",
      "authtoken": "y"
    },
    "request_body": {
      "id": "{{CHECKER-KEYID}}",
      "modNos": ["{{CHECKER-MODE-NEXT}}"],
      "remarks": "Approved"
    }
  }
  ```
- Success Condition:
  - Checker access update authorized.

