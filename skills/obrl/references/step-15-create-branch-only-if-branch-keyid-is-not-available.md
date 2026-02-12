### Step 15 — Create Branch (Only if BRANCH-KEYID is NOT available)
- Do not replace any json payload values.
- Tool Used:
  ```
  mcp restapi-mcp-server -> createRestAPICall
  ```
- Payload:
  ```json
  {
    "method": "POST",
    "action": "CREATE-BRANCH",
    "environment": "OBRL-14.8.2-RAH",
    "session": "{{SESSION_ID}}",
    "url": "{{CMC-BRANCH-SERVICES}}/corebranchs",
    "request_headers": {
      "Content-Type": "application/json",
      "appId": "CMNCORE",
      "userId": "{{MAKER-ID}}",
      "entityId": "DEFAULTENTITY",
      "authToken": "y",
      "branchCode": "{{DEFAULT-BRANCH-CODE}}"
    },
    "request_body": {
      "sourceBranchCode": "{{BRANCH-CODE}}",
      "sourceSystem": "FCUBS",
      "weekHol2": "7",
      "weekHol1": "1",
      "autoAuth": "N",
      "walkinCustomer": null,
      "branchLcy": "USD",
      "branchAddr3": "UK",
      "branchAddr2": "LANE 2",
      "branchAddr1": "LANE 1",
      "branchName": "{{BRANCH-NAME}}",
      "countryCode": "US",
      "hostCode": "HOST1",
      "branchCode": "{{BRANCH-CODE}}",
      "CoreBranchPrefDTO": {
        "branchCode": "{{BRANCH-CODE}}"
      },
      "CoreSwiftAddressDTO": [
        {
          "defaultBic": "Y",
          "swiftAddress": "NFCUUS33XXX",
          "branchCode": "{{BRANCH-CODE}}"
        }
      ]
    },
    "post_script": {
      "{{BRANCH-KEYID}}": "jq_expression('.messages.keyId', $RESPONSE_BODY)"
    }
  }
  ```
- Success Condition:
  - Branch created and `BRANCH-KEYID` stored.

