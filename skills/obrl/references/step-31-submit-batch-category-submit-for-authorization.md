### Step 31 — SUBMIT-BATCH-CATEGORY (Submit for Authorization)
- Do not replace any json payload values.
- Purpose:
  - Submit the newly created Branch Batch Category configuration for authorization.
- Execution Condition:
  - Execute only after Step 29 has completed (Populate Branch Batch Jobs) and when `SLPR_BATCHCATEGORY_RESPONSE_KEYID` and `BRANCH-CODE` are available.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "PATCH",
    "action": "SUBMIT-BATCH-CATEGORY",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{SLPR-BATCHCATEGORY-SERVICES}}/service/v14.8.1.0.0/batchcategories/{{SLPR_BATCHCATEGORY_RESPONSE_KEYID}}/submit",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{MAKER-ID}}",
      "branchCode": "{{BRANCH-CODE}}",
      "appId": "BATCHCATEGORY",
      "entityId": "DEFAULTENTITY"
    }
  }
  ```
- Success Condition:
  - If the http status code is in 2xx.

