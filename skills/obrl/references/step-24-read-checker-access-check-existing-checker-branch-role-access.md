### Step 24 — READ-CHECKER-ACCESS (Check existing Checker branch/role access)
- Execution Condition:
  - Execute only if `CHECKER-KEYID` is available in environment.
- Do not replace any json payload values.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "GET",
    "action": "READ-CHECKER-ACCESS",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{SMS-CORE-SERVICES}}/user/{{CHECKER-KEYID}}?version=latest",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{CHECKER-ID}}",
      "branchCode": "{{DEFAULT-BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY",
      "appId": "sms",
      "authtoken": "y"
    },
    "post_script": {
      "{{CHECKER-ACCESS-RAW}}": "$RESPONSE_BODY",
      "{{CHECKER-MODE-NEXT}}": "jq_expression('.data.modNo + 1', $RESPONSE_BODY)",
      "{{CHECKER-BRANCH-ACCESS-EXISTS}}": "jq_expression('((.data.UserRoleBranches // []) | map(.branchCode) | index(\"{{BRANCH-CODE}}\")) != null', $RESPONSE_BODY)",
      "{{NEW-CHECKER-ACCESS-DATA}}": "jq_expression('.data | .UserRoleBranches |= ( . + [{\"branchCode\":\"{{BRANCH-CODE}}\",\"branchId\":\"{{BRANCH-KEYID}}\",\"roleCode\":\"{{ROLE-SUPER_ADMIN-CODE}}\",\"roleId\":\"{{ROLE-SUPER_ADMIN-KEYID}}\",\"roleDescription\":\"{{ROLE-SUPER_ADMIN-DESC}}\"}] | unique_by(.branchCode))',$RESPONSE_BODY)"
    }
  }
  ```
- Success Condition:
  - `CHECKER-ACCESS-RAW` captured, `CHECKER-BRANCH-ACCESS-EXISTS` computed, `NEW-CHECKER-ACCESS-DATA` prepared, and `CHECKER-MODE-NEXT` computed.

