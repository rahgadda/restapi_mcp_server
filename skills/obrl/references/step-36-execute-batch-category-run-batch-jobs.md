### Step 36 — EXECUTE-BATCH-CATEGORY (Run Batch Jobs)
- Do not replace any json payload values.
- Purpose:
  - Execute the batch jobs created for the new branch.
- Execution Condition:
  - Execute only after Step 32 has authorized the batch category and after Step 34 validated branch date.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "POST",
    "action": "EXECUTE-BATCH-CATEGORY",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{SLPR-BATCHCATEGORY-SERVICES}}/service/v14.8.1.0.0/categoryexecutors/executeCategory",
    "request_headers": {
      "Content-Type": "application/json",
      "appId": "BATCHCATEGORY",
      "branchCode": "{{BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY",
      "userId": "{{MAKER-ID}}"
    },
    "request_body": {
      "categoryBranchCode":"{{BRANCH-CODE}}",
      "categoryCode":"CUTOFF",
      "runDate":"{{BRANCH-DATE}}",
      "isReRun": false,
      "reRunCause":"",
      "executeSingle": false
    }
  }
  ```
- Success Condition:
-  If the http status code is in 2xx.
