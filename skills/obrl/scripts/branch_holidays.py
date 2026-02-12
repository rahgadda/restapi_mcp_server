#!/usr/bin/env python3

import json
import calendar
import sys
from copy import deepcopy
from datetime import date
from urllib.request import Request, urlopen

MIN_YEAR = 2018
REST_API_ENDPOINT = "http://100.76.169.105:9090/api/v001/restapi/call"
REST_API_HEADERS = {"Content-Type": "application/json"}


# -----------------------------
# Date + Holiday Logic
# -----------------------------

def is_leap_year(y):
    return (y % 400 == 0) or (y % 4 == 0 and y % 100 != 0)


def month_len(y, m):
    return calendar.monthrange(y, m)[1]


def compute_anchor_date():
    today = date.today()
    first = today.replace(day=1)

    m = first.month - 3
    y = first.year
    if m <= 0:
        m += 12
        y -= 1

    if y < MIN_YEAR:
        y = MIN_YEAR

    return date(y, m, 1)


def generate_month(year, month, anchor):
    days = month_len(year, month)
    result = ["H"] * days

    # 30-Mar-2018 always Working
    if year == 2018 and month == 3:
        result[29] = "W"

    ay, am = anchor.year, anchor.month
    today = date.today()
    is_current_year = year == today.year
    is_current_month = is_current_year and month == today.month

    if year < ay:
        return "".join(result)
    if year == ay and month < am:
        return "".join(result)

    for offset in range(3):
        tm = am + offset
        ty = ay
        if tm > 12:
            tm -= 12
            ty += 1

        if year == ty and month == tm:
            for d in [1, 13, 14, 15, 16, 17]:
                if 1 <= d <= days:
                    result[d - 1] = "W"

    # if current month/year, mark days after today as working
    if is_current_month:
        for idx in range(today.day, days):
            result[idx] = "W"

    return "".join(result)


def generate_holidays(year, overrides):
    if year < MIN_YEAR:
        year = MIN_YEAR

    anchor = compute_anchor_date()
    out = {}
    today = date.today()
    is_current_year = year == today.year

    for m in range(1, 13):
        key = f"HOLIDAY-M{m:02}"
        if key in overrides and overrides[key]:
            month_value = overrides[key]
        else:
            month_value = generate_month(year, m, anchor)

        if is_current_year:
            days_in_month = month_len(year, m)
            if m > today.month:
                month_value = "W" * days_in_month
            elif m == today.month:
                month_chars = list(month_value)
                if len(month_chars) < days_in_month:
                    month_chars.extend(["H"] * (days_in_month - len(month_chars)))
                month_chars = month_chars[:days_in_month]
                for idx in range(today.day, days_in_month):
                    month_chars[idx] = "W"
                month_value = "".join(month_chars)

        out[key] = month_value

    return out


# -----------------------------
# HTTP Helper
# -----------------------------

def http_call(payload):
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        REST_API_ENDPOINT,
        data=body,
        headers=REST_API_HEADERS,
        method="POST",
    )
    with urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    # restapi orchestrator responses wrap the downstream payload inside
    # response_status/response_body; fall back to legacy shape otherwise.
    if "response_status" in result:
        status = result.get("response_status")
        body = result.get("response_body") or {}
        if not (200 <= status < 300):
            raise RuntimeError(
                f"REST call failed with status {status}: {json.dumps(body)}"
            )
        return body

    return result


# -----------------------------
# Main Runner
# -----------------------------
def main(create_file, authorize_file):
    with open(create_file) as f:
        create_template = json.load(f)

    with open(authorize_file) as f:
        authorize_template = json.load(f)

    anchor_year = compute_anchor_date().year
    current_year = date.today().year
    end_year = max(anchor_year, current_year)
    years = range(MIN_YEAR, end_year + 1)

    for year in years:
        create_payload = json.loads(json.dumps(create_template).replace("{{HOLIDAY-YEAR}}", str(year)))
        authorize_payload = deepcopy(authorize_template)

        overrides = {}
        for item in create_payload["request_body"]["CmcTmLocalHolidayDto"]:
            placeholder = item.get("holidayList")
            if isinstance(placeholder, str) and placeholder.startswith("{{HOLIDAY-M"):
                item["holidayList"] = None
            if item["holidayList"]:
                overrides[f"HOLIDAY-M{int(item['month']):02}"] = item["holidayList"]

        computed = generate_holidays(year, overrides)

        for item in create_payload["request_body"]["CmcTmLocalHolidayDto"]:
            m = int(item["month"])
            item["holidayList"] = computed[f"HOLIDAY-M{m:02}"]

        create_resp = http_call(create_payload)

        key_id = create_resp["messages"]["keyId"]
        # key_id = "rahul-test-key-id"  # Placeholder for testing
        # print(f"Generated Body create_payload[\"request_body\"] = {create_payload['request_body']}")
        print(f"Created Branch Holiday KeyID: {key_id} for year {year}")

        authorize_payload["url"] = authorize_payload["url"].replace("{{BRANCH-HOLIDAY-KEYID}}", str(key_id))
        authorize_payload["request_body"]["id"] = str(key_id)

        http_call(authorize_payload)
        # print(f"Generated Body authorize_payload[\"request_body\"] = {authorize_payload['request_body']}")
        print(f"Authorized Branch Holiday KeyID: {key_id} for year {year}")


# -----------------------------
# Entry Point
# -----------------------------

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 branch_holidays.py holiday_template.json holiday_authorization_template.json")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
