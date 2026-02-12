### Step 20 — READ-MAKER-ACCESS (Check existing Maker branch/role access)
- Execution Condition:
  - Execute only if `MAKER-KEYID` is available in environment.
- Do not replace any json payload values.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "GET",
    "action": "READ-MAKER-ACCESS",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{SMS-CORE-SERVICES}}/user/{{MAKER-KEYID}}?version=latest",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{MAKER-ID}}",
      "branchCode": "{{DEFAULT-BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY",
      "appId": "sms",
      "authtoken": "y"
    },
    "post_script": {
      "{{MAKER-ACCESS-RAW}}": "$RESPONSE_BODY",
      "{{MAKER-MODE-NEXT}}": "jq_expression('.data.modNo + 1', $RESPONSE_BODY)",
      "{{MAKER-BRANCH-ACCESS-EXISTS}}": "jq_expression('((.data.UserRoleBranches // []) | map(.branchCode) | index(\"{{BRANCH-CODE}}\")) != null', $RESPONSE_BODY)",
      "{{NEW-MAKER-ACCESS-DATA}}": "jq_expression('.data | .UserRoleBranches |= ( . + [{\"branchCode\":\"{{BRANCH-CODE}}\",\"branchId\":\"{{BRANCH-KEYID}}\",\"roleCode\":\"{{ROLE-SUPER_ADMIN-CODE}}\",\"roleId\":\"{{ROLE-SUPER_ADMIN-KEYID}}\",\"roleDescription\":\"{{ROLE-SUPER_ADMIN-DESC}}\"}] | unique_by(.branchCode))',$RESPONSE_BODY)"
    }
  }
  ```
- Post Script details:
  - `MAKER-ACCESS-RAW` stores the full response body for downstream processing (uses `$RESPONSE_BODY`).
  - `MAKER-MODE-NEXT` is computed from response body using jq path `.data.modNo + 1` and stored for the next update request.
  - `MAKER-BRANCH-ACCESS-EXISTS` is a boolean computed by jq (null-safe):
    - Expression: `((.data.UserRoleBranches // []) | map(.branchCode) | index("{{BRANCH-CODE}}")) != null`
    - true means the Maker already has access to the target branch; false means it is missing.
  - `NEW-MAKER-ACCESS-DATA` is an array computed by jq from `.data.UserRoleBranches`. If the target branch is missing, the array is appended with one node having:
    ```json
    {
      "branchCode": "{{BRANCH-CODE}}",
      "branchId": "{{BRANCH-KEYID}}",
      "roleCode": "{{ROLE-SUPER_ADMIN-CODE}}",
      "roleId": "{{ROLE-SUPER_ADMIN-KEYID}}",
      "roleDescription": "{{ROLE-SUPER_ADMIN-DESC}}"
    }
    ```
- Success Condition:
  - `MAKER-ACCESS-RAW` captured, `MAKER-BRANCH-ACCESS-EXISTS` computed, `NEW-MAKER-ACCESS-DATA` prepared, and `MAKER-MODE-NEXT` computed.


