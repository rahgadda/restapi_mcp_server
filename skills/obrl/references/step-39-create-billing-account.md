### Step 39 — CREATE-BILLING-ACCOUNT
- Do not replace any json payload values.

- Purpose:
  - Create a lending billing account using the previously created party and persist `{{BILLING-ACCOUNT-KEYID}}` via `post_script`.

- Pre‑step: Compute and save `FIRST-INSTALLMENT-DATE`
  - Read `BRANCH-DATE` from the environment store:
    - Tool: `mcp restapi-mcp-server -> listSpecificEnvironmentVariable`
    - Inputs: `environment`, `variable = BRANCH-DATE`
  - Compute `FIRST-INSTALLMENT-DATE = BRANCH-DATE + 1 month` (ISO `YYYY-MM-DD`). Examples:
    - macOS: `date -j -f "%Y-%m-%d" "$BRANCH_DATE" -v+1m "+%Y-%m-%d"`
    - GNU/Linux: `date -d "$BRANCH_DATE +1 month" +%F`
  - Save to environment store:
    - Tool: `mcp restapi-mcp-server -> upsertEnvironmentVariable`
    - Inputs: `environment`, `variable = FIRST-INSTALLMENT-DATE`, `value = <computed date>`
  - Result: `{{FIRST-INSTALLMENT-DATE}}` available for request body.

- Execution Condition:
  - Execute when `{{PARTY-KEYID}}` exists (from Step 38), and `{{BRANCH-DATE}}` is available.
  - Seeded variables from Step 3: `{{MAKER-ID}}`, `{{CHECKER-ID}}`, `{{BRANCH-CODE}}`, `{{OBRL-LN-ACCOUNT-SERVICES}}`, `{{AOB-BILLING-LEDGER}}`.
  - Input variable present as applicable: `{{FIRST-INSTALLMENT-DATE}}`.
  - Active `session` exists (Step 7).

- Tool Used:
  - Local script wrapper
    - Script: `scripts/create_billing_account.sh`
    - Template: `scripts/create_billing_account.template.json`
  - Example: `bash scripts/create_billing_account.sh {{SESSION}} http://100.76.169.105:9090/api/v001/restapi/call`

- Payload Template (excerpt header):
  ```json
  {
    "method": "POST",
    "action": "CREATE-BILLING-ACCOUNT",
    "session": "{{SESSION_ID}}",
    "url": "{{OBRL-LN-ACCOUNT-SERVICES}}/service/v14.8.2.0.0/accounts/accountCreate",
    "request_headers": { /* ... */ },
    "request_body": { /* body uses PARTY-KEYID, BRANCH-DATE, FIRST-INSTALLMENT-DATE, AOB-BILLING-LEDGER */ },
    "post_script": {
      "{{BILLING-ACCOUNT-KEYID}}": "jq_expression('.data.accountNumber', $RESPONSE_BODY)"
    }
  }
  ```

- Success Criteria:
  - HTTP status is 2xx.
  - `{{BILLING-ACCOUNT-KEYID}}` appears in the environment via orchestrator upsert.

- Troubleshooting:
  - If `.data.accountNumber` is empty, verify the API response structure and that prerequisite variables are set.
  - Confirm `FIRST-INSTALLMENT-DATE` is provided in environment and matches expected format (YYYY-MM-DD).
  - Ensure `AOB-BILLING-LEDGER` is seeded and valid.
