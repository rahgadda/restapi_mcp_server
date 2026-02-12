### Step 16 — Authorize Branch (only if a new branch was created in Step 15)
- Do not replace any json payload values.
- Execution Condition:
  - Run this step only when Step 15 created a new branch (`BRANCH-KEYID` was set by Step 15). If `BRANCH-KEYID` already existed before Step 15, skip this step.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "PATCH",
    "action": "AUTHORIZE-BRANCH",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{CMC-BRANCH-SERVICES}}/corebranchs/{{BRANCH-KEYID}}/approve",
    "request_headers": {
      "Content-Type": "application/json",
      "appId": "CMNCORE",
      "userId": "{{CHECKER-ID}}",
      "entityId": "DEFAULTENTITY",
      "authToken": "y",
      "branchCode": "{{DEFAULT-BRANCH-CODE}}"
    },
    "request_body": {
      "id": "{{BRANCH-KEYID}}",
      "modNos": [1],
      "remarks": "approved"
    }
  }
  ```
- Success Condition:
  - Branch approval request submitted.

