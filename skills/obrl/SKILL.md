---
name: OBRL
description: "OBRL REST API Test Orchestrator"
id: "obrl"
version: "1.0.0"
summary: "Validates and prepares an OBRL test environment via Docker, MCP, env vars, session management, and REST API execution."
mcp_name: "restapi-mcp-server"
---

# OBRL
This skill validates and prepares an OBRL test environment using a structured, step-by-step workflow with strict state validation and non-interactive execution.

The agent is state-aware, step-validated, and non-interactive:
- It verifies prerequisites in order.
- If a required input or state is missing, execution stops with a clear failure.
- The agent does not ask for user input during execution; steps are executed strictly based on user-provided inputs.
- The user can start from any step; the agent will backtrack and validate all required previous steps.
- Do not replace any json payload values.

## Skill Name
OBRL REST API Test Orchestrator

## Skill Objective
Validate infrastructure readiness and execute OBRL REST API test preparation using:
- MCP (restapi-mcp-server)
- Environment variables
- Session management
- REST API execution

## Behavior Rules
Full rules and exceptions moved to [references/behavior-rules.md](references/behavior-rules.md).
Summary: sequential (1-36), non-interactive, stop on missing state; reuse validated steps; strict payload/variable constraints;.

## REST API JSON Contract (Alignment with server)
The rest API call contract must follow the server schema:
- method: string (GET, POST, PUT, PATCH, DELETE)
- url: string
- session: string
- environment: string
- action: string
- request_headers: object (optional)
- request_body: object (optional)
- post_script: object (optional) mapping output variable names to expressions

Interpolation and post-script rules:
- Use `{{VARIABLE_NAME}}` directly for environment variables.
- Base64 helpers: use `base64_encode(...)` or `base64_decode(...)` without outer `{{ }}`. Example: `"username": "base64_encode({{MAKER-ID}})"`.
- To extract from the latest HTTP response, use `jq_expression('<jq filter>', $RESPONSE_BODY)` in post_script values.
- In `post_script`, the keys are variable names to upsert; they can be plain (`"DEFAULT-BRANCH-DATE"`).

Payload construction constraints:
- Only include fields explicitly shown in the payload templates in this SKILL.md for that step.
- Do not add new properties to request_headers, request_body, or post_script that are not present in the template.
- Only replace placeholders inside << >>; all other literal values must remain unchanged.
- If a required placeholder variable is unavailable, stop execution; do not attempt to create undeclared variables or alter the payload shape.

## Step-by-Step Workflow

### Step 1 — Check MCP Registration
- MCP Name:
  ```
  restapi-mcp-server
  ```
- Validation:
  - Verify MCP is registered and reachable.
- If not registered:
  - Stop execution; MCP must be registered and reachable.

### Step 2 — Reset Environment Variables
- Tool Used:
  ```
  mcp restapi-mcp-server -> deleteAllByEnvironment
  ```
- Inputs:
  - environment: OBRL-14.8.2-RAH
- Action:
  - Delete all stored environment variables for `OBRL-14.8.2-RAH` to ensure a clean state before seeding.
- Failure:
  - Stop execution if deletion fails; environment must be reset cleanly.

### Step 3 — Create Session
- Validation:
  - Check if a session already exists.
- If not:
  - Create a new session using:
    ```
    mcp restapi-mcp-server -> createSession
    ```
- Store:
  - Store the created session id in `{{SESSION_ID}}` for subsequent steps by persisting it to the environment variable store using:
    ```
    mcp restapi-mcp-server -> createEnvironmentVariables

    {
      "items": [
       {"environment": "OBRL-14.8.2-RAH", "variable": "SESSION_ID", "value": "<<replace this value with session id from createSession response>>"}
      ]
    }
    ```

### Step 4 — ENV_ID Constant
- Instruction:
  - Treat `ENV_ID` or environment as `OBRL-14.8.2-RAH` for all remaining steps. When an environment identifier is required, reference this exact value without creating or modifying any environment store entries in this step.

### Step 5 — Seed Environment Variables via Terminal Playwright Command
- Tool Used:
  - Local terminal running `npx playwright open`
- Action:
  - Open a terminal on the host machine and run:
    ```
    npx playwright open http://100.76.169.105:5500/
    ```
  - Leave the spawned Playwright browser window open until all required seeding actions are complete and closed manually.
  - Immediately switch the Playwright window into fullscreen mode (macOS shortcut: `⌃⌘F`; Windows/Linux: `F11`) and keep it fullscreen for the duration of the seeding session.
- Wait/Resume behavior:
  - Continue automatically to Step 6 once the terminal command exits (which only happens after the browser window is closed). No prompts or confirmations are issued.
- Success criteria:
  - The terminal command finishes successfully because the user closed the Playwright window.

### Step 6 — List Environment Variables
- Tool Used:
  ```
  mcp restapi-mcp-server -> listAllEnvironmentVariables
  ```
- Inputs:
  - environment: OBRL-14.8.2-RAH
- Action:
  - Fetch and store available environment variables for that environment.

### Step 7 — Validate DEFAULT-BRANCH-CODE
- Validation:
  - Confirm `DEFAULT-BRANCH-CODE` exists in environment variables.
- If missing:
  - Stop execution; DEFAULT-BRANCH-CODE is required.

### Step 9 — Populate DEFAULT-BRANCH-DATE
- Summary: Fetch branch system date and store {{DEFAULT-BRANCH-DATE}}.
Full payload and details moved to [references/step-08-populate-default-branch-date.md](references/step-08-populate-default-branch-date.md).

### Step 10 — Validate DEFAULT-BRANCH-DATE
- Summary: Verify {{DEFAULT-BRANCH-DATE}} exists in the environment.
Full payload and details moved to [references/step-09-validate-default-branch-date.md](references/step-09-validate-default-branch-date.md).

### Step 11 — Populate MAKER-TOKEN
- Summary: Create maker JWT token and store {{MAKER-TOKEN}}.
Full payload and details moved to [references/step-10-populate-maker-token.md](references/step-10-populate-maker-token.md).

### Step 12 — Validate MAKER-TOKEN
- Summary: Verify {{MAKER-TOKEN}} exists in the environment.
Full payload and details moved to [references/step-11-validate-maker-token.md](references/step-11-validate-maker-token.md).

### Step 13 — Populate CHECKER-TOKEN
- Summary: Create checker JWT token and store {{CHECKER-TOKEN}}.
Full payload and details moved to [references/step-12-populate-checker-token.md](references/step-12-populate-checker-token.md).

### Step 14 — Validate CHECKER-TOKEN
- Summary: Verify {{CHECKER-TOKEN}} exists in the environment.
Full payload and details moved to [references/step-13-validate-checker-token.md](references/step-13-validate-checker-token.md).

### Step 15 — Check Existing BRANCH-KEYID (Get for Branch KeyID)
- Summary: Check if {{BRANCH-KEYID}} already exists, if yes then skip creation.
Full payload and details moved to [references/step-14-check-existing-branch-keyid-gate-for-branch-creation.md](references/step-14-check-existing-branch-keyid-gate-for-branch-creation.md).

### Step 16 — Create Branch (Only if BRANCH-KEYID is NOT available)
- Summary: Create a new branch and capture {{BRANCH-KEYID}}.
Full payload and details moved to [references/step-15-create-branch-only-if-branch-keyid-is-not-available.md](references/step-15-create-branch-only-if-branch-keyid-is-not-available.md).

### Step 17 — Authorize Branch (only if a new branch was created in Step 16)
- Summary: Authorize the newly created branch using {{BRANCH-KEYID}}.
Full payload and details moved to [references/step-16-authorize-branch-only-if-a-new-branch-was-created-in-step-15.md](references/step-16-authorize-branch-only-if-a-new-branch-was-created-in-step-15.md).

### Step 18 — Validate BRANCH-KEYID (Post Creation/Authorization)
- Summary: Verify {{BRANCH-KEYID}} is present for downstream steps.
Full payload and details moved to [references/step-17-validate-branch-keyid-post-creation-authorization.md](references/step-17-validate-branch-keyid-post-creation-authorization.md).

### Step 19 — GET-MAKER-UUID (If Step 16 completed OR MAKER-KEYID is not available)
- Summary: Lookup maker user and store {{MAKER-KEYID}}.
Full payload and details moved to [references/step-18-get-maker-uuid-if-step-15-completed-or-maker-keyid-is-not-available.md](references/step-18-get-maker-uuid-if-step-15-completed-or-maker-keyid-is-not-available.md).

### Step 20 — GET-ROLE-UUID (Only if ROLE-SUPER_ADMIN-KEYID is not available)
- Summary: Fetch SUPER_ADMIN role; store key, code, and description.
Full payload and details moved to [references/step-19-get-role-uuid-only-if-role-super-admin-keyid-is-not-available.md](references/step-19-get-role-uuid-only-if-role-super-admin-keyid-is-not-available.md).

### Step 21 — READ-MAKER-ACCESS (Check existing Maker branch/role access)
- Summary: Read maker access; compute next mod and prepare updated branches.
Full payload and details moved to [references/step-20-read-maker-access-check-existing-maker-branch-role-access.md](references/step-20-read-maker-access-check-existing-maker-branch-role-access.md).

### Step 22 — UPDATE-MAKER-BRANCH-ACCESS (Upsert Maker branch/role access)
- Summary: Upsert maker branch/role access with prepared data.
Full payload and details moved to [references/step-21-update-maker-branch-access-upsert-maker-branch-role-access.md](references/step-21-update-maker-branch-access-upsert-maker-branch-role-access.md).

### Step 23 — AUTHORIZE-MAKER-ACCESS (Authorize updated user access)
- Summary: Authorize maker access update using computed modNos.
Full payload and details moved to [references/step-22-authorize-maker-access-authorize-updated-user-access.md](references/step-22-authorize-maker-access-authorize-updated-user-access.md).

### Step 24 — GET-CHECKER-UUID (If Step 16 completed OR CHECKER-KEYID is not available)
- Summary: Lookup checker user and store {{CHECKER-KEYID}}.
Full payload and details moved to [references/step-23-get-checker-uuid-if-step-15-completed-or-checker-keyid-is-not-available.md](references/step-23-get-checker-uuid-if-step-15-completed-or-checker-keyid-is-not-available.md).

### Step 25 — READ-CHECKER-ACCESS (Check existing Checker branch/role access)
- Summary: Read checker access; compute next mod and prepare update data.
Full payload and details moved to [references/step-24-read-checker-access-check-existing-checker-branch-role-access.md](references/step-24-read-checker-access-check-existing-checker-branch-role-access.md).

### Step 26 — UPDATE-CHECKER-BRANCH-ACCESS (Upsert Checker branch/role access)
- Summary: Upsert checker branch/role access with prepared data.
Full payload and details moved to [references/step-25-update-checker-branch-access-upsert-checker-branch-role-access.md](references/step-25-update-checker-branch-access-upsert-checker-branch-role-access.md).

### Step 27 — AUTHORIZE-CHECKER-ACCESS (Authorize updated Checker access)
- Summary: Authorize checker access update using computed modNos.
Full payload and details moved to [references/step-26-authorize-checker-access-authorize-updated-checker-access.md](references/step-26-authorize-checker-access-authorize-updated-checker-access.md).

### Step 28 — Create + Authorize Branch Holidays
- Summary: Create and authorize branch holidays for the new branch.
- Execution Condition: Run only if Step 16 created a new branch (i.e., Step 15 did not find an existing BRANCH-KEYID).
- Tool Used: Local Python script
  - Location: `scripts/`
  - Command:
    ```
    cd scripts && python3 branch_holidays.py holiday_template.json holiday_authorization_template.json
    ```
    (Both template files reside alongside the script; adjust the working directory if invoking differently.)
  - Success Criteria:
    - Script must finish without errors (exit code 0); proceed to Step 30 only after a successful run.
    - On failure, stop the workflow and do not continue to downstream steps.

### Step 29 — Create Branch Batch Jobs (SLPR_BATCHCATEGORY)
- Check if all holidays are created in step 27 before starting Step 29.
- Summary: Initiate SLPR batch category job creation; store response key.
Full payload and details moved to [references/step-29-create-branch-batch-jobs-slpr-batchcategory.md](references/step-29-create-branch-batch-jobs-slpr-batchcategory.md).

### Step 30 — Populate Branch Batch Jobs (POPULATE-BATCH-CATEGORY)
- Purpose: Populate batch categories for the branch.
- Why script: The MCP single-call payload exceeds gateway limits; use a local curl wrapper to post the full body.
- Preconditions: Step 29 completed; `BRANCH-CODE`, `SLPR_BATCHCATEGORY_RESPONSE_KEYID`, and `MAKER-ID` available in the selected environment.

- Tool Used: Local script wrapper
  - Script: `scripts/create_batch_categories.sh`
  - Usage: `bash scripts/create_batch_categories.sh <session> [restapi_url]`
    - `session` (required): orchestrator session id; substitutes the `__SESSION__` placeholder in the template.
    - `restapi_url` (optional): override orchestrator endpoint (defaults to `http://100.76.169.105:9090/api/v001/restapi/call`)
  - Note:
    - The request template already contains any required `environment` / `session` values directly; the script posts the JSON as-is.

- Example:
  - `bash scripts/create_batch_categories.sh {{SESSION}} http://100.76.169.105:9090/api/v001/restapi/call`

- Success Criteria:
  - HTTP status is in the 2xx range (script exits 0). Non‑2xx must stop the flow.

- Next:
  - Proceed to Step 32 only if Step 31 succeeded.

### Step 31 — SUBMIT-BATCH-CATEGORY (Submit for Authorization)
- Summary: Submit the populated batch category for authorization.
 - Execution Condition: Run only if Step 31 succeeded (HTTP 2xx from script).
Full payload and details moved to [references/step-31-submit-batch-category-submit-for-authorization.md](references/step-31-submit-batch-category-submit-for-authorization.md).

### Step 32 — AUTHORIZE-BATCH-CATEGORY
- Summary: Authorize the submitted batch category configuration.
 - Execution Condition: Run only if Step 31 succeeded (HTTP 2xx from script).
Full payload and details moved to [references/step-32-authorize-batch-category.md](references/step-32-authorize-batch-category.md).

### Step 33 — GET_NEW_BRANCH_SYSTEM_DATES (Get New Branch GL Date)
- Summary: Fetch the new branch GL date and store {{BRANCH-DATE}}.
 - Execution Condition: Run only if Step 31 succeeded (HTTP 2xx from script).
Full payload and details moved to [references/step-33-get-new-branch-system-dates-get-new-branch-gl-date.md](references/step-33-get-new-branch-system-dates-get-new-branch-gl-date.md).

### Step 34 — VALIDATE-BRANCH-DATE
- Summary: Verify {{BRANCH-DATE}} exists in the environment.
 - Execution Condition: Run only if Step 31 succeeded (HTTP 2xx from script).
Full payload and details moved to [references/step-34-validate-branch-date.md](references/step-34-validate-branch-date.md).

### Step 35 — UPDATE-BRANCH-DATE
- Summary: Perform branch date progression via sequential operations (MARK_CUTOFF → MARK_EOFI → FLIPDATE → RELEASE_CUTOFF → MARK_TI). Stop on first failure.
Full payload and details moved to [references/step-35-update-branch-date.md](references/step-35-update-branch-date.md).

### Step 36 — RE-UPDATE_NEW_BRANCH_SYSTEM_DATES (Re-update New Branch GL Date)
- Summary: Fetch the new branch GL date and store {{BRANCH-DATE}}.
 - Execution Condition: Run only if Step 36 succeeded (HTTP 2xx from script).
Full payload and details moved to [references/step-36-reupdate-new-branch-system-date.md](references/step-36-reupdate-new-branch-system-date.md).

### Step 37 — AUTO_NUMBER_GENERATION
- Summary: Create and authorize Auto Number Generation for accounts.
- Execution Condition: Run Authorize only if Create returned HTTP 2xx and `{{AUTONUMBER-KEYID}}` exists in the environment store.
Full payload and details moved to [references/step-37-auto-number-generation.md](references/step-37-auto-number-generation.md).

### Step 38 — CREATE-PARTY
- Summary: Create a retail party and store `{{PARTY-KEYID}}`.
Full payload and details moved to [references/step-38-create-party.md](references/step-38-create-party.md).

### Step 39 — CREATE-BILLING-ACCOUNT
- Pre-step: Compute and save `FIRST-INSTALLMENT-DATE`
  - Tool Used:
    - `mcp restapi-mcp-server -> listSpecificEnvironmentVariable` (read `BRANCH-DATE`)
    - Compute `FIRST-INSTALLMENT-DATE = BRANCH-DATE + 1 month` (ISO `YYYY-MM-DD`).
      - macOS: `date -j -f "%Y-%m-%d" "$BRANCH_DATE" -v+1m "+%Y-%m-%d"`
      - GNU/Linux: `date -d "$BRANCH_DATE +1 month" +%F`
    - `mcp restapi-mcp-server -> upsertEnvironmentVariable` (write `FIRST-INSTALLMENT-DATE`).
  - Result:
    - `{{FIRST-INSTALLMENT-DATE}}` available for the payload in this step.
- Summary: Create a billing account and store `{{BILLING-ACCOUNT-KEYID}}`.
Full payload and details moved to [references/step-39-create-billing-account.md](references/step-39-create-billing-account.md).

### Step 40 — Execution Summary
- Summary: Render a run summary table and optional HTML export.
Full payload and details moved to [references/step-40-execution-summary.md](references/step-40-execution-summary.md).
