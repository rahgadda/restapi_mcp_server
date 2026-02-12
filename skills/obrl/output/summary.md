| S.No | Description | Action Code | Status |
| ---- | ----------- | ----------- | ------ |
| 1 | Check MCP registration | MCP_HEALTH | Success |
| 2 | Reset environment variables | deleteAllByEnvironment | Success |
| 3 | Create orchestrator session | createSession | Success |
| 4 | Set ENV_ID constant | ENV_ID | Success |
| 5 | Run Playwright seeding | PLAYWRIGHT_OPEN | Success |
| 6 | List environment variables | listAllEnvironmentVariables | Success |
| 7 | Validate DEFAULT-BRANCH-CODE | listSpecificEnvironmentVariable | Success |
| 8 | Populate DEFAULT-BRANCH-DATE | GET_BRANCH_SYSTEM_DATES | Success |
| 9 | Validate DEFAULT-BRANCH-DATE | listSpecificEnvironmentVariable | Success |
| 10 | Populate MAKER-TOKEN | CREATE-MAKER-USER-TOKEN | Success |
| 11 | Validate MAKER-TOKEN | listSpecificEnvironmentVariable | Success |
| 12 | Populate CHECKER-TOKEN | CREATE-CHECKER-USER-TOKEN | Success |
| 13 | Validate CHECKER-TOKEN | listSpecificEnvironmentVariable | Success |
| 14 | Check existing BRANCH-KEYID | listSpecificEnvironmentVariable | Success |
| 15 | Create Branch | CREATE-BRANCH | Success |
| 16 | Authorize Branch | AUTHORIZE-BRANCH | Success |
| 17 | Validate BRANCH-KEYID | listSpecificEnvironmentVariable | Success |
| 18 | Get Maker UUID | GET-MAKER-UUID | Success |
| 19 | Get SUPER_ADMIN role | GET-ROLE-UUID | Success |
| 20 | Read Maker access | READ-MAKER-ACCESS | Success |
| 21 | Update Maker access | UPDATE-MAKER-ACCESS | Success |
| 22 | Authorize Maker access | AUTHORIZE-MAKER-ACCESS | Success |
| 23 | Get Checker UUID | GET-CHECKER-UUID | Success |
| 24 | Read Checker access | READ-CHECKER-ACCESS | Success |
| 25 | Update Checker access | UPDATE-CHECKER-ACCESS | Success |
| 26 | Authorize Checker access | AUTHORIZE-CHECKER-ACCESS | Success |
| 27 | Create & authorize branch holidays | CREATE-BRANCH-HOLIDAYS/AUTHORIZE-BRANCH-HOLIDAYS | Success |
| 28 | Create branch batch jobs | CREATE-BRANCH-BATCH-JOBS-SLPR-BATCHCATEGORY | Success |
| 29 | Populate batch categories | POPULATE-BATCH-CATEGORY | Success |
| 30 | Submit batch category | SUBMIT-BATCH-CATEGORY | Success |
| 31 | Authorize batch category | AUTHORIZE-BATCH-CATEGORY | Success |
| 32 | Get branch GL date | GET_NEW_BRANCH_SYSTEM_DATES | Success |
| 33 | Validate branch date | listSpecificEnvironmentVariable | Success |
| 34 | Update branch date sequence | MARK_CUTOFF/MARK_EOFI/FLIPDATE/RELEASE_CUTOFF/MARK_TI | Success |
| 35 | Refresh branch GL date | REUPDATE_NEW_BRANCH_SYSTEM_DATES | Success |
| 36 | Auto number create/authorize | POPULATE-AUTONUMBER/AUTHORIZE-AUTONUMBER | Success |
| 37 | Create party | CREATE-PARTY | Success |
| 38 | Compute first installment | FIRST-INSTALLMENT-DATE | Success |
| 39 | Create billing account | CREATE-BILLING-ACCOUNT | Success |
| 40 | Execution summary & artifacts | SUMMARY-GENERATION | Success |
