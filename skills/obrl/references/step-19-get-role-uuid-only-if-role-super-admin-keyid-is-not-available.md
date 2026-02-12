### Step 19 — GET-ROLE-UUID (Only if ROLE-SUPER_ADMIN-KEYID is not available)
- Execution Condition:
  - Execute only if `ROLE-SUPER_ADMIN-KEYID` is not available in environment.
- Do not replace any json payload values.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "GET",
    "action": "GET-ROLE-UUID",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{SMS-CORE-SERVICES}}/role?roleCode=SUPER_ADMIN",
    "request_headers": {
      "Content-Type": "application/json",
      "userId": "{{MAKER-ID}}",
      "branchCode": "{{DEFAULT-BRANCH-CODE}}",
      "entityId": "DEFAULTENTITY",
      "appId": "sms",
      "authtoken": "y"
    },
    "post_script": {
      "{{ROLE-SUPER_ADMIN-KEYID}}": "jq_expression('.data[0].keyId', $RESPONSE_BODY)",
      "{{ROLE-SUPER_ADMIN-DESC}}": "jq_expression('.data[0].description', $RESPONSE_BODY)",
      "{{ROLE-SUPER_ADMIN-CODE}}": "jq_expression('.data[0].roleCode', $RESPONSE_BODY)"
    }
  }
  ```
- Success Condition:
  - `ROLE-SUPER_ADMIN-KEYID`, `ROLE-SUPER_ADMIN-DESC`, and `ROLE-SUPER_ADMIN-CODE` stored in env store.

