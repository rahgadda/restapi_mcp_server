### Step 8 — Populate DEFAULT-BRANCH-DATE
- Do not replace any json payload values.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "GET",
    "action": "GET_BRANCH_SYSTEM_DATES",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{CMC-BRANCH-SERVICES}}/systemdates?includecloseandunauth=false&offset=0&limit=1&branchCode={{DEFAULT-BRANCH-CODE}}",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{MAKER-ID}}",
      "appId": "CMNCORE",
      "branchCode": "{{DEFAULT-BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY"
    },
    "post_script": {
      "{{DEFAULT-BRANCH-DATE}}": "jq_expression('.data[0].today', $RESPONSE_BODY)"
    }
  }
  ```
- Success Condition:
  - `DEFAULT-BRANCH-DATE` stored in env store.

