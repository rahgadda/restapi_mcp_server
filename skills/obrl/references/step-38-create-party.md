### Step 38 — CREATE-PARTY
- Do not replace any json payload values.

- Purpose:
  - Create a retail party and persist `{{PARTY-KEYID}}` to the environment store via `post_script`.

- Execution Condition:
  - Execute when `{{BRANCH-DATE}}`, `{{MAKER-ID}}`, `{{BRANCH-CODE}}`, and `{{OBPY-PARTY-SERVICES}}` are available.
  - Active `session` exists (Step 7).

- Tool Used:
  - Local script wrapper
    - Script: `scripts/create_party.sh`
    - Template: `scripts/create_party.template.json`
  - Example: `bash scripts/create_party.sh {{SESSION}} http://100.76.169.105:9090/api/v001/restapi/call`

- Payload Template (excerpt header):
  ```json
  {
    "method": "POST",
    "action": "POPULATE-BATCH-CATEGORY",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{SLPR-BATCHCATEGORY-SERVICES}}/service/v14.8.1.0.0/batchcategories",
    "request_headers": { /* ... */ },
    "request_body": { /* very large body; unchanged except placeholders */ },
    "post_script": {
      "{{PARTY-KEYID}}": "jq_expression('.messages.keyId', $RESPONSE_BODY)"
    }
  }
  ```

- Success Criteria:
  - HTTP status is 2xx.
  - `{{PARTY-KEYID}}` appears in the environment via orchestrator upsert.

- Troubleshooting:
  - Ensure `BRANCH-DATE` exists (Step 33/36). Missing date placeholders will cause validation failures.
  - Check that `OBPY-PARTY-SERVICES` is seeded in Step 3.
  - Inspect orchestrator response file printed by the script; verify `.messages.keyId`.

