### Step 29 — Create Branch Batch Jobs (SLPR_BATCHCATEGORY)
- Do not replace any json payload values.
- Purpose:
  - Initiate branch batch jobs for SLPR_BATCHCATEGORY.
- Execution Condition:
  - Execute only after Step 27 has completed (Branch Holidays) and when `BRANCH-CODE` is available.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "POST",
    "action": "CREATE-BRANCH-BATCH-JOBS-SLPR-BATCHCATEGORY",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{CMC-RESOURCE-SEGMENT-ORCHESTRATOR-SERVICE}}/web/orchestrator/initiate/SLPR_BATCHCATEGORY",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{MAKER-ID}}",
      "branchCode": "{{BRANCH-CODE}}",
      "appId": "CMNCORE",
      "entityId": "DEFAULTENTITY",
      "authToken": "y"
    },
    "post_script": {
      "{{SLPR_BATCHCATEGORY_RESPONSE_KEYID}}": "jq_expression('.data.resourceId', $RESPONSE_BODY)"
    }
  }
  ```
- Success Condition:
  - `SLPR_BATCHCATEGORY_RESPONSE_KEYID` stored in env store.

