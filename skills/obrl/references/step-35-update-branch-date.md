### Step 35 — UPDATE-BRANCH-DATE
- Do not replace any json payload values.
- Purpose:
  - Progress the branch to the next business date by invoking a sequence of branch-date operations.
- Execution Condition:
  - Run only after Step 34 has validated `BRANCH-DATE`.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```

- Sequence (stop on first failure):
  1) MARK_CUTOFF
  2) MARK_EOFI
  3) FLIPDATE
  4) RELEASE_CUTOFF
  5) MARK_TI

- Payloads:
  ```json
  {
    "method": "POST",
    "action": "MARK_CUTOFF",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{CMC-BRANCH-SERVICES}}/batch/markcutoff?eodBranch={{BRANCH-CODE}}",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{MAKER-ID}}",
      "appId": "CMNCORE",
      "branchCode": "{{BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY"
    }
  }
  ```

  ```json
  {
    "method": "POST",
    "action": "MARK_EOFI",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{CMC-BRANCH-SERVICES}}/batch/markeofi?eodBranch={{BRANCH-CODE}}",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{MAKER-ID}}",
      "appId": "CMNCORE",
      "branchCode": "{{BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY"
    }
  }
  ```

  ```json
  {
    "method": "POST",
    "action": "FLIPDATE",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{CMC-BRANCH-SERVICES}}/batch/flipdate",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{MAKER-ID}}",
      "appId": "CMNCORE",
      "branchCode": "{{BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY"
    }
  }
  ```

  ```json
  {
    "method": "POST",
    "action": "RELEASE_CUTOFF",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{CMC-BRANCH-SERVICES}}/batch/releasecutoff?eodBranch={{BRANCH-CODE}}",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{MAKER-ID}}",
      "appId": "CMNCORE",
      "branchCode": "{{BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY"
    }
  }
  ```

  ```json
  {
    "method": "POST",
    "action": "MARK_TI",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{CMC-BRANCH-SERVICES}}/batch/markti?eodBranch={{BRANCH-CODE}}",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{MAKER-ID}}",
      "appId": "CMNCORE",
      "branchCode": "{{BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY"
    }
  }
  ```

- Success Condition:
  - Each call must return HTTP 2xx. On non‑2xx, stop immediately and fail the skill.

