## Step 27 — Create + Authorize Branch Holidays (Dynamic, System-Date Driven)

### Purpose

Create branch-level holiday configuration using deterministic rules derived from the **current system date**, generating monthly Working/Holiday (`W` / `H`) strings for a given year, and immediately authorize each created holiday entry.

---

### Preconditions

* `BRANCH-KEYID` is validated (Step 17)
* `BRANCH-CODE` exists (Step 15 or earlier)
* Checker access update completed (Step 26)

---

### Inputs

* No user input required
* All values are derived unless explicitly overridden:

  * `HOLIDAY-YEAR`
  * `HOLIDAY-M01` … `HOLIDAY-M12`

---

### Date Anchors

* `SYSTEM_DATE` = current system date
* `FIRST_OF_SYSTEM_DATE` = first day of `SYSTEM_DATE` month
* `ANCHOR_DATE` = first day of (`FIRST_OF_SYSTEM_DATE` − 3 months)
* `ANCHOR-YEAR`, `ANCHOR-MONTH` derived from `ANCHOR_DATE`

> Minimum supported year: **2018**
> Any computed year < 2018 must be treated as **2018**

---

### Working / Holiday Rules

#### Explicit Working Days

* **30-Mar-2018** is always `W`
* For the **ANCHOR month and next two months** (with year rollover):

  * Day **1**
  * Days **13–17**
  * All marked as `W`

#### Holidays

* All other days are `H`
* All days **before ANCHOR_DATE** are `H` (except 30-Mar-2018)

---

### Year-Based Generation Rules

For each `HOLIDAY-YEAR = Y`:

#### If `Y < ANCHOR-YEAR`

* All months → all days `H`

#### If `Y == ANCHOR-YEAR`

* Months `< ANCHOR-MONTH` → all `H`
* Months `>= ANCHOR-MONTH`:

  * Days 13–17 → `W`
  * All others → `H`

#### If `Y > ANCHOR-YEAR`

* Default all months → all `H` (unless overridden)

---

### Month String Constraints

* `HOLIDAY-M01 … HOLIDAY-M12`
* Length must match actual month length (leap years included)
* Allowed values: only `W` or `H`

**Leap Year Rule**

```
(Y % 400 == 0) OR (Y % 4 == 0 AND Y % 100 != 0)
```

---

### Overrides

* Any explicitly provided `HOLIDAY-MXX` value **wins** over computed values.

---

### Fixed Values

* `weeklyHolidays = "N"`
* `unexpHol = "N"`

---

### Tool Invocation

```
mcp restapi-mcp-server → createRestAPICall (CREATE)
mcp restapi-mcp-server → createRestAPICall (AUTHORIZE)
```

---

### Payloads

> Replace **only** values inside `<< >>` or `{{ }}` (env/session variables).
> Do **not** modify static JSON fields.

```json
{
  "method": "POST",
  "action": "CREATE-BRANCH-HOLIDAYS",
  "environment": "OBRL-14.8.2-RAH",
  "session": "<<session id>>",
  "url": "{{CMC-BRANCH-SERVICES}}/localholidays",
  "request_headers": {
    "Content-Type": "application/json",
    "appId": "CMNCORE",
    "userId": "{{MAKER-ID}}",
    "entityId": "DEFAULTENTITY",
    "authToken": "y",
    "branchCode": "{{DEFAULT-BRANCH-CODE}}"
  },
  "request_body": {
    "branchCode": "{{BRANCH-CODE}}",
    "year": "{{HOLIDAY-YEAR}}",
    "weeklyHolidays": "N",
    "unexpHol": "N",
    "CmcTmLocalHolidayDto": [
      { "month": 1,  "branchCode": "{{BRANCH-CODE}}", "year": "{{HOLIDAY-YEAR}}", "holidayList": "{{HOLIDAY-M01}}"},
      { "month": 2,  "branchCode": "{{BRANCH-CODE}}", "year": "{{HOLIDAY-YEAR}}", "holidayList": "{{HOLIDAY-M02}}" },
      { "month": 3,  "branchCode": "{{BRANCH-CODE}}", "year": "{{HOLIDAY-YEAR}}", "holidayList": "{{HOLIDAY-M03}}" },
      { "month": 4,  "branchCode": "{{BRANCH-CODE}}", "year": "{{HOLIDAY-YEAR}}", "holidayList": "{{HOLIDAY-M04}}" },
      { "month": 5,  "branchCode": "{{BRANCH-CODE}}", "year": "{{HOLIDAY-YEAR}}", "holidayList": "{{HOLIDAY-M05}}" },
      { "month": 6,  "branchCode": "{{BRANCH-CODE}}", "year": "{{HOLIDAY-YEAR}}", "holidayList": "{{HOLIDAY-M06}}" },
      { "month": 7,  "branchCode": "{{BRANCH-CODE}}", "year": "{{HOLIDAY-YEAR}}", "holidayList": "{{HOLIDAY-M07}}" },
      { "month": 8,  "branchCode": "{{BRANCH-CODE}}", "year": "{{HOLIDAY-YEAR}}", "holidayList": "{{HOLIDAY-M08}}" },
      { "month": 9,  "branchCode": "{{BRANCH-CODE}}", "year": "{{HOLIDAY-YEAR}}", "holidayList": "{{HOLIDAY-M09}}" },
      { "month": 10, "branchCode": "{{BRANCH-CODE}}", "year": "{{HOLIDAY-YEAR}}", "holidayList": "{{HOLIDAY-M10}}" },
      { "month": 11, "branchCode": "{{BRANCH-CODE}}", "year": "{{HOLIDAY-YEAR}}", "holidayList": "{{HOLIDAY-M11}}" },
      { "month": 12, "branchCode": "{{BRANCH-CODE}}", "year": "{{HOLIDAY-YEAR}}", "holidayList": "{{HOLIDAY-M12}}" }
    ],
    "doerRemarks": ""
  },
  "post_script": {
    "{{BRANCH-HOLIDAY-KEYID}}": "jq_expression('.messages.keyId', $RESPONSE_BODY)"
  }
}
```

Immediately after a successful CREATE, call AUTHORIZE for the captured keyId:

```json
{
  "method": "PATCH",
  "action": "AUTHORIZE-BRANCH-HOLIDAYS",
  "environment": "OBRL-14.8.2-RAH",
  "session": "<<session id created or available>>",
  "url": "{{CMC-BRANCH-SERVICES}}/localholidays/{{BRANCH-HOLIDAY-KEYID}}/approve",
  "request_headers": {
    "Content-Type": "application/json",
    "appId": "CMNCORE",
    "userId": "{{CHECKER-ID}}",
    "entityId": "DEFAULTENTITY",
    "authToken": "y",
    "branchCode": "{{DEFAULT-BRANCH-CODE}}"
  },
  "request_body": {
    "id": "{{BRANCH-HOLIDAY-KEYID}}",
    "modNos": [1],
    "remarks": "approved"
  }
}
```

---

### Success Criteria

* Branch holidays created and authorized successfully for each processed year/branch
* Valid API responses received
* `BRANCH-HOLIDAY-KEYID` captured and authorized
