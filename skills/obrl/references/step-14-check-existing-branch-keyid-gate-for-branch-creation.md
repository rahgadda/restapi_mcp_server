### Step 14 — Check Existing BRANCH-KEYID (Gate for Branch Creation)
- Purpose:
  - Prevent unnecessary branch creation if one already exists.
- Tool Used:
  ```
  mcp restapi-mcp-server -> listSpecificEnvironmentVariable
  ```
- Inputs:
  - variable: `BRANCH-KEYID`
- Validation:
  - Check if `BRANCH-KEYID` exists and is non-empty.
- Control Flow:
  - If `BRANCH-KEYID` exists:
    - Do NOT create a new branch.
    - Do NOT authorize.
    - Proceed directly to Step 18 (Validate BRANCH-KEYID).
  - If `BRANCH-KEYID` does not exist:
    - Proceed to Step 16 (Create Branch), then Step 17 (Authorize Branch).

