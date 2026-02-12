### Step 21 — UPDATE-MAKER-BRANCH-ACCESS (Upsert Maker branch/role access)
- Do not replace any json payload values.
- Execution Condition:
  - Execute only if `MAKER-KEYID` is available, `NEW-MAKER-ACCESS-DATA` is computed in Step 20, and `MAKER-BRANCH-ACCESS-EXISTS` is false.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "PUT",
    "action": "UPDATE-MAKER-ACCESS",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{SMS-CORE-SERVICES}}/user/{{MAKER-KEYID}}",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{TEMP-MAKER-ID}}",
      "branchCode": "{{DEFAULT-BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY",
      "appId": "sms",
      "authtoken": "y"
    },
    "request_body": "{{NEW-MAKER-ACCESS-DATA}}"
  }
  ```
- Success Condition:
  - Maker access updated for the target branch/role combination.

