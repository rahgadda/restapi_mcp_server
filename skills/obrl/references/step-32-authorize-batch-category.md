### Step 32 — AUTHORIZE-BATCH-CATEGORY
- Do not replace any json payload values.
- Purpose:
  - Authorize the submitted Branch Batch Category configuration.
- Execution Condition:
  - Execute only after Step 31 has completed (Submit Batch Category) and when `SLPR_BATCHCATEGORY_RESPONSE_KEYID` and `BRANCH-CODE` are available.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "PUT",
    "action": "AUTHORIZE-BATCH-CATEGORY",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{SLPR-BATCHCATEGORY-SERVICES}}/service/v14.8.1.0.0/batchcategories/{{SLPR_BATCHCATEGORY_RESPONSE_KEYID}}/authorize",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{CHECKER-ID}}",
      "branchCode": "{{BRANCH-CODE}}",
      "appId": "BATCHCATEGORY",
      "entityId": "DEFAULTENTITY"
    },
    "request_body": {
      "resourceId": "{{SLPR_BATCHCATEGORY_RESPONSE_KEYID}}",
      "modNos": [1],
      "remarks": "approved",
      "screenClassCode": "SLPR_BATCHCATEGORY"
    }
  }
  ```
- Success Condition:
  - If the http status code is in 2xx.

