### Step 40 — Execution Summary
- Purpose:
  - Provide a final human-readable summary of all steps executed (or skipped) during this run.
- Execution Condition:
  - Always execute after stopping (success or failure). This step performs no external calls and produces output only.
- Output:
  1. Print the Markdown table with columns: S.No | Description | Action Code | Status (example header below).
  2. When `TEMP-STORAGE-DIR` is available, write the same Markdown table to `{{TEMP-STORAGE-DIR}}/summary.md`.
  3. Immediately run `python3 scripts/summary_to_html.py --dir {{TEMP-STORAGE-DIR}}` to build the interactive dashboard at `{{TEMP-STORAGE-DIR}}/formatted.html`. This HTML output is the primary artifact for run review.
  4. Launch a Playwright browser (same pattern as Step 5) to open `formatted.html` by running `npx playwright open file://{{TEMP-STORAGE-DIR}}/formatted.html` and keep it open for stakeholders to review before closing manually.
  - Example Markdown header row:
    | S.No | Description | Action Code | Status |
    | ---- | ----------- | -------------- | ------ |
- Tool Used:
  ```
  mcp restapi-mcp-server -> listSpecificEnvironmentVariable (read-only for `TEMP-STORAGE-DIR`)
  python3 scripts/summary_to_html.py --dir <dir containing summary.md>
  npx playwright open file://<dir>/formatted.html
  ```
- Population Rules:
  - Include rows for steps 1..36 that were in scope of this run.
  - Description: short name of the step (e.g., "Create Branch", "Authorize Branch Holidays").
  - Action Code: Key identifiers provided in each json payload. Example record value as EXECUTE-BATCH-CATEGORY for input having "action": "EXECUTE-BATCH-CATEGORY".
- Notes:
  - Do not mutate environment or perform API calls in this step; render output only. File writes to `{{TEMP-STORAGE-DIR}}/summary.md`, generates `{{TEMP-STORAGE-DIR}}/formatted.html`, and displays it via the Playwright browser session.
