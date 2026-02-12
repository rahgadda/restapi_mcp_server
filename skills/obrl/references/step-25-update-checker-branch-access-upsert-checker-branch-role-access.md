### Step 25 — UPDATE-CHECKER-BRANCH-ACCESS (Upsert Checker branch/role access)
- Do not replace any json payload values.
- Execution Condition:
  - Execute only if `CHECKER-KEYID` is available, `NEW-CHECKER-ACCESS-DATA` is computed in Step 24, and `CHECKER-BRANCH-ACCESS-EXISTS` is false.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "PUT",
    "action": "UPDATE-CHECKER-ACCESS",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{SMS-CORE-SERVICES}}/user/{{CHECKER-KEYID}}",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{TEMP-MAKER-ID}}",
      "branchCode": "{{DEFAULT-BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY",
      "appId": "sms",
      "authtoken": "y"
    },
    "request_body": "{{NEW-CHECKER-ACCESS-DATA}}"
  }
  ```
- Success Condition:
  - Checker access updated for the target branch/role combination.

