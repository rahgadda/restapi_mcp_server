### Step 36 — REUPDATE_NEW_BRANCH_SYSTEM_DATES (Re-update New Branch GL Date)
- Do not replace any json payload values.
- Purpose:
  - Fetch the branch date after update branch date after (Step 35)
- Execution Condition:
  - Execute only after Step 35 has completed (Update Branch Date) and when `BRANCH-CODE` is available.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "GET",
    "action": "REUPDATE_NEW_BRANCH_SYSTEM_DATES",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{CMC-BRANCH-SERVICES}}/systemdates?includecloseandunauth=false&offset=0&limit=1&branchCode={{BRANCH-CODE}}",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{MAKER-ID}}",
      "appId": "CMNCORE",
      "branchCode": "{{BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY"
    },
    "post_script": {
      "{{BRANCH-DATE}}": "jq_expression('.data[0].today', $RESPONSE_BODY)"
    }
  }
  ```
- Success Condition:
  - `BRANCH-DATE` stored in env store.

